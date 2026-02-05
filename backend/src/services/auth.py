"""Authentication service for JWT token management and password hashing."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import RefreshToken, User

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Bcrypt-hashed password to check against.

    Returns:
        True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: UUID,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User's unique identifier (becomes 'sub' claim).
        email: User's email address.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT access token string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    # Use timezone-aware UTC datetime for correct timestamp calculation
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def verify_access_token(token: str) -> dict:
    """
    Verify and decode a JWT access token.

    Args:
        token: JWT access token string.

    Returns:
        Decoded payload dictionary with claims.

    Raises:
        JWTError: If token is invalid, expired, or has wrong type.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )

    # Verify token type
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")

    return payload


def _hash_token(token: str) -> str:
    """
    Hash a refresh token for secure storage.

    Args:
        token: Raw token string.

    Returns:
        SHA-256 hash of the token.
    """
    return hashlib.sha256(token.encode()).hexdigest()


async def create_refresh_token(
    session: AsyncSession,
    user_id: UUID,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a refresh token and store its hash in the database.

    Args:
        session: Database session.
        user_id: User's unique identifier.
        expires_delta: Optional custom expiration time.

    Returns:
        Raw refresh token string (to be stored in HTTP-only cookie).
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.refresh_token_expire_days)

    # Generate a secure random token
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)

    # Calculate expiration in UTC, but store as naive datetime for SQLite compatibility
    expires_at = (datetime.now(timezone.utc) + expires_delta).replace(tzinfo=None)

    # Create and store the refresh token record
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    session.add(refresh_token)
    await session.flush()

    # Return raw token with embedded token ID for lookup
    # Format: <token_id>.<random_token>
    return f"{refresh_token.id}.{raw_token}"


async def _get_refresh_token_record(
    session: AsyncSession,
    token_string: str
) -> Optional[RefreshToken]:
    """
    Parse token string and retrieve the refresh token record from database.

    Args:
        session: Database session.
        token_string: Token string in format "<token_id>.<random_token>".

    Returns:
        RefreshToken record if found and hash matches, None otherwise.
    """
    try:
        # Parse token format: <token_id>.<random_token>
        parts = token_string.split(".", 1)
        if len(parts) != 2:
            return None

        token_id_str, raw_token = parts
        token_id = UUID(token_id_str)
        token_hash = _hash_token(raw_token)

        # Fetch the token record
        result = await session.execute(
            select(RefreshToken).where(RefreshToken.id == token_id)
        )
        token_record = result.scalar_one_or_none()

        if token_record is None:
            return None

        # Verify the hash matches
        if token_record.token_hash != token_hash:
            return None

        return token_record

    except (ValueError, AttributeError):
        return None


async def rotate_refresh_token(
    session: AsyncSession,
    old_token_string: str
) -> Optional[tuple[str, User]]:
    """
    Rotate a refresh token: invalidate the old one and create a new one.

    Args:
        session: Database session.
        old_token_string: Current refresh token string.

    Returns:
        Tuple of (new_token_string, user) if successful, None if token is invalid.
    """
    # Get the old token record
    old_token = await _get_refresh_token_record(session, old_token_string)

    if old_token is None:
        return None

    # Verify token is still valid
    if not old_token.is_valid():
        return None

    # Get the user
    result = await session.execute(
        select(User).where(User.id == old_token.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    # Create new token
    new_token_string = await create_refresh_token(session, user.id)

    # Parse new token to get its ID for the replaced_by reference
    new_token_id = UUID(new_token_string.split(".", 1)[0])

    # Invalidate old token
    old_token.revoke(replaced_by_id=new_token_id)

    return new_token_string, user


async def revoke_refresh_token(
    session: AsyncSession,
    token_string: str
) -> bool:
    """
    Revoke a refresh token (for logout).

    Args:
        session: Database session.
        token_string: Refresh token string to revoke.

    Returns:
        True if token was found and revoked, False otherwise.
    """
    token_record = await _get_refresh_token_record(session, token_string)

    if token_record is None:
        return False

    # Token might already be revoked, but that's okay
    if token_record.revoked_at is None:
        token_record.revoke()

    return True


async def validate_refresh_token(
    session: AsyncSession,
    token_string: str
) -> Optional[User]:
    """
    Validate a refresh token and return the associated user.

    Args:
        session: Database session.
        token_string: Refresh token string to validate.

    Returns:
        User if token is valid, None otherwise.
    """
    token_record = await _get_refresh_token_record(session, token_string)

    if token_record is None:
        return None

    if not token_record.is_valid():
        return None

    # Get the user
    result = await session.execute(
        select(User).where(User.id == token_record.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    return user
