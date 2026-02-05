"""Authentication API endpoints for JWT-based authentication."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.exceptions import EmailExistsError, InvalidCredentialsError
from src.core.rate_limit import limiter
from src.db.session import get_session
from src.models.user import User
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)
from src.api.deps import CurrentUser

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Request/Response Models


class UserCreate(BaseModel):
    """Request model for user registration."""

    email: EmailStr = Field(..., max_length=255, description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (8-128 characters)",
    )


class UserResponse(BaseModel):
    """Response model for user data."""

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """Response model for login with tokens."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshResponse(BaseModel):
    """Response model for token refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Response model for simple messages."""

    message: str


# Endpoints


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Email already registered"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("3/hour")
async def register(
    request: Request,
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """
    Register a new user account.

    - **email**: Valid email address (max 255 characters)
    - **password**: Password (8-128 characters)
    """
    # Normalize email to lowercase
    email = user_data.email.lower()

    # Check if email already exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise EmailExistsError()

    # Create new user with hashed password
    user = User(
        email=email,
        password_hash=hash_password(user_data.password),
    )

    session.add(user)
    await session.flush()

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """
    Authenticate user and receive access token.

    Returns access token in response body and sets refresh token as HTTP-only cookie.
    """
    # Normalize email to lowercase
    email = login_data.email.lower()

    # Find user by email
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Verify credentials (same error for wrong email or password)
    if user is None or not verify_password(login_data.password, user.password_hash):
        raise InvalidCredentialsError()

    if not user.is_active:
        raise InvalidCredentialsError()

    # Create tokens
    access_token = create_access_token(user.id, user.email)
    refresh_token = await create_refresh_token(session, user.id)

    # Set refresh token as HTTP-only cookie
    # Use samesite="none" for cross-origin requests (frontend on Vercel, backend on Render)
    # secure=True is required when samesite="none"
    is_production = settings.environment != "development"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="none" if is_production else "lax",
        path="/api/auth",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {"description": "Invalid or expired refresh token"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit("30/minute")
async def refresh(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefreshResponse:
    """
    Refresh access token using refresh token from cookie.

    Rotates the refresh token (old token becomes invalid, new token issued).
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Refresh token not provided"},
        )

    # Rotate refresh token
    result = await rotate_refresh_token(session, refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_EXPIRED", "message": "Refresh token is invalid or expired"},
        )

    new_refresh_token, user = result

    # Create new access token
    access_token = create_access_token(user.id, user.email)

    # Update refresh token cookie
    # Use samesite="none" for cross-origin requests (frontend on Vercel, backend on Render)
    is_production = settings.environment != "development"
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=is_production,
        samesite="none" if is_production else "lax",
        path="/api/auth",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return RefreshResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageResponse:
    """
    Logout user by revoking refresh token and clearing cookie.

    Requires valid access token.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        # Revoke the refresh token in database
        await revoke_refresh_token(session, refresh_token)

    # Clear the refresh token cookie
    # Must match the same cookie settings used when setting it
    is_production = settings.environment != "development"
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth",
        httponly=True,
        secure=is_production,
        samesite="none" if is_production else "lax",
    )

    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """
    Get current authenticated user's information.

    Requires valid access token.
    """
    return UserResponse.model_validate(current_user)
