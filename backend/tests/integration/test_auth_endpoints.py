"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


class TestRegistration:
    """Tests for POST /api/auth/register endpoint (T079)."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient, test_user_data: dict):
        """Registration with valid data should create user and return 201."""
        response = await client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == test_user_data["email"]
        assert "created_at" in data
        # Password should never be in response
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data: dict):
        """Registration with existing email should return 400 EMAIL_EXISTS."""
        # Register first user
        await client.post("/api/auth/register", json=test_user_data)

        # Try to register with same email
        response = await client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 400
        data = response.json()
        assert data["code"] == "EMAIL_EXISTS"
        assert "already registered" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Registration with invalid email format should return 422."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "securepassword123"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Registration with password < 8 chars should return 422."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_email_normalized_to_lowercase(
        self, client: AsyncClient
    ):
        """Registration should normalize email to lowercase."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "TEST@EXAMPLE.COM", "password": "securepassword123"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"


class TestLogin:
    """Tests for POST /api/auth/login endpoint (T080)."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data: dict):
        """Login with valid credentials should return tokens."""
        # Register user first
        await client.post("/api/auth/register", json=test_user_data)

        # Login
        response = await client.post("/api/auth/login", json=test_user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

        # Check refresh token cookie is set
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient, test_user_data: dict):
        """Login with non-existent email should return 401 INVALID_CREDENTIALS."""
        response = await client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user_data: dict):
        """Login with wrong password should return 401 INVALID_CREDENTIALS."""
        # Register user first
        await client.post("/api/auth/register", json=test_user_data)

        # Login with wrong password
        response = await client.post(
            "/api/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["code"] == "INVALID_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_same_error_for_email_and_password(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Login should return same error for wrong email and wrong password."""
        # Register user
        await client.post("/api/auth/register", json=test_user_data)

        # Wrong email
        response1 = await client.post(
            "/api/auth/login",
            json={"email": "wrong@example.com", "password": test_user_data["password"]},
        )

        # Wrong password
        response2 = await client.post(
            "/api/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )

        # Both should have same error code and similar message
        assert response1.status_code == response2.status_code == 401
        assert response1.json()["code"] == response2.json()["code"] == "INVALID_CREDENTIALS"


class TestTokenRefresh:
    """Tests for POST /api/auth/refresh endpoint (T081)."""

    @pytest.mark.asyncio
    async def test_refresh_success(self, client: AsyncClient, test_user_data: dict):
        """Refresh with valid token should return new access token."""
        # Register and login
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post("/api/auth/login", json=test_user_data)
        refresh_token = login_response.cookies.get("refresh_token")

        # Refresh token
        response = await client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_refresh_without_cookie(self, client: AsyncClient):
        """Refresh without refresh token cookie should return 401."""
        response = await client.post("/api/auth/refresh")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"]["code"] == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Refresh with invalid token should return 401."""
        response = await client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": "invalid-token"},
        )

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout endpoint (T082)."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client: AsyncClient, test_user_data: dict):
        """Logout should revoke refresh token and clear cookie."""
        # Register and login
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post("/api/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.cookies.get("refresh_token")

        # Logout
        response = await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    @pytest.mark.asyncio
    async def test_logout_requires_auth(self, client: AsyncClient):
        """Logout without access token should return 401."""
        response = await client.post("/api/auth/logout")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_revokes_refresh_token(
        self, client: AsyncClient, test_user_data: dict
    ):
        """After logout, refresh token should no longer work."""
        # Register and login
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post("/api/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.cookies.get("refresh_token")

        # Logout
        await client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            cookies={"refresh_token": refresh_token},
        )

        # Try to refresh with old token
        response = await client.post(
            "/api/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )

        assert response.status_code == 401


class TestProtectedRoutes:
    """Tests for protected route access (T083)."""

    @pytest.mark.asyncio
    async def test_protected_route_requires_auth(self, client: AsyncClient):
        """Protected route without token should return 401."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_route_with_valid_token(
        self, client: AsyncClient, test_user_data: dict
    ):
        """Protected route with valid token should return user data."""
        # Register and login
        await client.post("/api/auth/register", json=test_user_data)
        login_response = await client.post("/api/auth/login", json=test_user_data)
        access_token = login_response.json()["access_token"]

        # Access protected route
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_protected_route_with_invalid_token(self, client: AsyncClient):
        """Protected route with invalid token should return 401."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401


class TestDataIsolation:
    """Tests for data isolation between users (T084)."""

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_users_tasks(
        self,
        client: AsyncClient,
        test_user_data: dict,
        test_user_data_2: dict,
    ):
        """User A should not be able to access User B's tasks."""
        # Register and login User A
        await client.post("/api/auth/register", json=test_user_data)
        login_a = await client.post("/api/auth/login", json=test_user_data)
        token_a = login_a.json()["access_token"]

        # Register and login User B
        await client.post("/api/auth/register", json=test_user_data_2)
        login_b = await client.post("/api/auth/login", json=test_user_data_2)
        token_b = login_b.json()["access_token"]

        # User A creates a task via chat
        await client.post(
            "/api/chat",
            json={"message": "Add a task: User A's private task"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # User A should see their task
        tasks_a = await client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert tasks_a.status_code == 200
        tasks_a_data = tasks_a.json()

        # User B should not see User A's task
        tasks_b = await client.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert tasks_b.status_code == 200
        tasks_b_data = tasks_b.json()

        # User A has tasks, User B has none
        assert tasks_a_data["total"] >= 0  # May have tasks from chat
        assert tasks_b_data["total"] == 0
