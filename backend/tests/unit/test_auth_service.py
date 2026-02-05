"""Unit tests for the authentication service."""

import pytest
from datetime import timedelta
from uuid import uuid4

from jose import jwt, JWTError

from src.core.config import settings
from src.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)


class TestPasswordHashing:
    """Tests for password hashing functions (T076)."""

    def test_hash_password_returns_hash(self):
        """hash_password should return a bcrypt hash string."""
        password = "securepassword123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        # bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")

    def test_hash_password_different_for_same_input(self):
        """hash_password should return different hashes for same password (due to salt)."""
        password = "securepassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """verify_password should return True for correct password."""
        password = "securepassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password should return False for incorrect password."""
        password = "securepassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """verify_password should return False for empty password."""
        password = "securepassword123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_hash_password_handles_special_characters(self):
        """hash_password should handle passwords with special characters."""
        password = "P@$$w0rd!#%^&*()"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_handles_unicode(self):
        """hash_password should handle unicode passwords."""
        password = "密码123パスワード"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True


class TestAccessToken:
    """Tests for access token functions (T077)."""

    def test_create_access_token_returns_jwt(self):
        """create_access_token should return a valid JWT string."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)

        assert token is not None
        assert isinstance(token, str)
        # JWT has 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_create_access_token_contains_correct_claims(self):
        """create_access_token should include correct claims in the token."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)

        # Decode without verification to check claims
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["type"] == "access"
        assert "iat" in payload
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """create_access_token should respect custom expiration delta."""
        user_id = uuid4()
        email = "test@example.com"
        expires_delta = timedelta(minutes=5)

        token = create_access_token(user_id, email, expires_delta)

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Check that exp - iat is approximately 5 minutes (300 seconds)
        time_diff = payload["exp"] - payload["iat"]
        assert 299 <= time_diff <= 301  # Allow 1 second tolerance

    def test_verify_access_token_valid(self):
        """verify_access_token should return payload for valid token."""
        user_id = uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)
        payload = verify_access_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["type"] == "access"

    def test_verify_access_token_invalid_signature(self):
        """verify_access_token should raise JWTError for invalid signature."""
        user_id = uuid4()
        email = "test@example.com"

        # Create token with different secret
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "iat": 1000000000,
            "exp": 9999999999,
        }
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")

        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_verify_access_token_expired(self):
        """verify_access_token should raise JWTError for expired token."""
        user_id = uuid4()
        email = "test@example.com"

        # Create already expired token
        token = create_access_token(user_id, email, timedelta(seconds=-10))

        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_verify_access_token_wrong_type(self):
        """verify_access_token should raise JWTError for non-access token type."""
        user_id = uuid4()
        email = "test@example.com"

        # Create token with wrong type
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "refresh",  # Wrong type
            "iat": 1000000000,
            "exp": 9999999999,
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_verify_access_token_malformed(self):
        """verify_access_token should raise JWTError for malformed token."""
        with pytest.raises(JWTError):
            verify_access_token("not-a-valid-jwt")

    def test_verify_access_token_empty(self):
        """verify_access_token should raise JWTError for empty token."""
        with pytest.raises(JWTError):
            verify_access_token("")


class TestRefreshTokenOperations:
    """Tests for refresh token operations (T078).

    Note: These tests require database access and are marked as integration tests.
    The actual async tests should be run with pytest-asyncio.
    """

    def test_refresh_token_hash_is_deterministic(self):
        """Token hash function should be deterministic for same input."""
        from src.services.auth import _hash_token

        token = "test-token-value"
        hash1 = _hash_token(token)
        hash2 = _hash_token(token)

        assert hash1 == hash2

    def test_refresh_token_hash_different_for_different_input(self):
        """Token hash function should produce different hashes for different inputs."""
        from src.services.auth import _hash_token

        hash1 = _hash_token("token1")
        hash2 = _hash_token("token2")

        assert hash1 != hash2

    def test_refresh_token_hash_is_sha256(self):
        """Token hash should be a 64-character hex string (SHA-256)."""
        from src.services.auth import _hash_token

        token_hash = _hash_token("test-token")

        assert len(token_hash) == 64
        assert all(c in "0123456789abcdef" for c in token_hash)
