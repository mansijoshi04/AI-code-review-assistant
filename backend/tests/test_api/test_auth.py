"""
Integration tests for authentication API endpoints.
"""

from app.models.user import User


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_create_token_new_user(self, client, db_session):
        """Test creating token for new user."""
        response = client.post(
            "/api/auth/token",
            params={
                "github_id": 99999,
                "username": "newuser",
                "email": "new@example.com",
                "avatar_url": "https://avatar.url",
                "access_token": "github_token",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify user was created
        user = db_session.query(User).filter(User.github_id == 99999).first()
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"

    def test_create_token_existing_user(self, client, db_session, test_user):
        """Test creating token for existing user updates their info."""
        response = client.post(
            "/api/auth/token",
            params={
                "github_id": test_user.github_id,
                "username": "updated_username",
                "email": "updated@example.com",
                "avatar_url": "https://new-avatar.url",
                "access_token": "new_github_token",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        # Verify user was updated
        db_session.refresh(test_user)
        assert test_user.username == "updated_username"
        assert test_user.email == "updated@example.com"
        assert test_user.access_token == "new_github_token"

    def test_create_token_minimal_data(self, client, db_session):
        """Test creating token with only required fields."""
        response = client.post(
            "/api/auth/token",
            params={
                "github_id": 88888,
                "username": "minimaluser",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

        # Verify user was created with minimal data
        user = db_session.query(User).filter(User.github_id == 88888).first()
        assert user is not None
        assert user.username == "minimaluser"
        assert user.email is None
        assert user.avatar_url is None

    def test_get_current_user_info(self, client, test_user, auth_headers):
        """Test getting current authenticated user info."""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["github_id"] == test_user.github_id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "access_token" not in data  # Should not expose sensitive data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # FastAPI returns 403 for missing auth

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed authorization header."""
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 403

    def test_token_contains_user_data(self, client, db_session):
        """Test that created token contains correct user data."""
        response = client.post(
            "/api/auth/token",
            params={
                "github_id": 77777,
                "username": "tokenuser",
            },
        )

        assert response.status_code == 200
        token = response.json()["access_token"]

        # Use token to get user info
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)

        assert me_response.status_code == 200
        data = me_response.json()
        assert data["github_id"] == 77777
        assert data["username"] == "tokenuser"
