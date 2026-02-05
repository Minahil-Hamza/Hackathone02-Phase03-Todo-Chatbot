"""FastAPI dependencies for authentication and authorization."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.models.user import User
from src.services.auth import verify_access_token

logger = logging.getLogger(__name__)

# OAuth2 scheme for Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """
    Dependency that extracts and validates the access token,
    returning the current authenticated user.

    Args:
        token: JWT access token from Authorization header.
        session: Database session.

    Returns:
        Authenticated User object.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "INVALID_TOKEN",
            "message": "Could not validate credentials",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        logger.info(f"Received token: {token[:30]}..." if len(token) > 30 else f"Received token: {token}")
        payload = verify_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception

        user_id = UUID(user_id_str)
        logger.info(f"Token valid for user_id: {user_id}")
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise credentials_exception
    except ValueError as e:
        logger.warning(f"Invalid user_id format: {e}")
        raise credentials_exception

    # Fetch user from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "ACCOUNT_DISABLED",
                "message": "User account is disabled",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Type alias for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
