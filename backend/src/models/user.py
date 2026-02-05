"""User and authentication models for JWT authentication."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    Represents a registered user in the system.

    Attributes:
        id: Unique identifier for the user.
        email: User's email address (unique, case-insensitive).
        password_hash: bcrypt-hashed password (never exposed in API).
        is_active: Whether the account is active.
        created_at: When the account was created.
        updated_at: When the account was last modified.
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(
        max_length=255,
        index=True,
        unique=True,
        nullable=False
    )
    password_hash: str = Field(max_length=255, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()


class RefreshToken(SQLModel, table=True):
    """
    Represents an active refresh token stored in the database.

    Attributes:
        id: Token identifier (used as jti claim in JWT).
        user_id: Owner user's ID.
        token_hash: Hashed token value for secure storage.
        expires_at: When the token expires.
        created_at: When the token was created.
        revoked_at: When the token was revoked (NULL if active).
        replaced_by: ID of the token that replaced this one (for rotation tracking).
    """

    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )
    token_hash: str = Field(max_length=255, nullable=False, index=True)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    revoked_at: Optional[datetime] = Field(default=None, nullable=True)
    replaced_by: Optional[UUID] = Field(
        default=None,
        foreign_key="refresh_tokens.id",
        nullable=True
    )

    def is_valid(self) -> bool:
        """Check if the token is still valid (not revoked and not expired)."""
        if self.revoked_at is not None:
            return False
        # Compare with naive UTC datetime (stored as naive in DB)
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        if self.expires_at < now_utc:
            return False
        return True

    def revoke(self, replaced_by_id: Optional[UUID] = None) -> None:
        """Revoke this token, optionally linking to its replacement."""
        # Store as naive UTC datetime for SQLite compatibility
        self.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
        if replaced_by_id:
            self.replaced_by = replaced_by_id
