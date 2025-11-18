"""
Integration tests for repository API endpoints.
"""

import pytest
from app.models.repository import Repository
from app.core.security import create_user_token


@pytest.fixture
def test_repository(db_session, test_user):
    """Create a test repository."""
    repo = Repository(
        user_id=test_user.id,
        github_id=67890,
        name="test-repo",
        full_name="testuser/test-repo",
        owner="testuser",
        is_active=True,
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)
    return repo


class TestRepositoryEndpoints:
    """Tests for repository API endpoints."""

    def test_list_repositories_empty(self, client, auth_headers):
        """Test listing repositories when user has none."""
        response = client.get("/api/repositories", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["repositories"] == []

    def test_list_repositories(self, client, auth_headers, test_repository):
        """Test listing repositories."""
        response = client.get("/api/repositories", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["repositories"]) == 1
        assert data["repositories"][0]["id"] == str(test_repository.id)
        assert data["repositories"][0]["name"] == "test-repo"

    def test_list_repositories_pagination(
        self, client, auth_headers, test_user, db_session
    ):
        """Test repository listing with pagination."""
        # Create multiple repositories
        for i in range(5):
            repo = Repository(
                user_id=test_user.id,
                github_id=1000 + i,
                name=f"repo-{i}",
                full_name=f"testuser/repo-{i}",
                owner="testuser",
            )
            db_session.add(repo)
        db_session.commit()

        # Test with limit
        response = client.get(
            "/api/repositories", params={"limit": 3}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["repositories"]) == 3

        # Test with skip
        response = client.get(
            "/api/repositories", params={"skip": 2, "limit": 2}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["repositories"]) == 2

    def test_list_repositories_filter_active(
        self, client, auth_headers, test_user, db_session
    ):
        """Test filtering repositories by active status."""
        # Create active and inactive repositories
        active_repo = Repository(
            user_id=test_user.id,
            github_id=2000,
            name="active-repo",
            full_name="testuser/active-repo",
            owner="testuser",
            is_active=True,
        )
        inactive_repo = Repository(
            user_id=test_user.id,
            github_id=2001,
            name="inactive-repo",
            full_name="testuser/inactive-repo",
            owner="testuser",
            is_active=False,
        )
        db_session.add_all([active_repo, inactive_repo])
        db_session.commit()

        # Filter for active only
        response = client.get(
            "/api/repositories", params={"is_active": True}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["repositories"][0]["is_active"] is True

    def test_list_repositories_unauthorized(self, client):
        """Test listing repositories without authentication."""
        response = client.get("/api/repositories")

        assert response.status_code == 403

    def test_create_repository(self, client, auth_headers, test_user, db_session):
        """Test creating a new repository."""
        repo_data = {
            "github_id": 99999,
            "name": "new-repo",
            "full_name": "testuser/new-repo",
            "owner": "testuser",
            "is_active": True,
        }

        response = client.post(
            "/api/repositories", json=repo_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["github_id"] == 99999
        assert data["name"] == "new-repo"
        assert data["user_id"] == str(test_user.id)

        # Verify in database
        repo = db_session.query(Repository).filter(Repository.github_id == 99999).first()
        assert repo is not None
        assert repo.name == "new-repo"

    def test_create_repository_duplicate_github_id(
        self, client, auth_headers, test_repository
    ):
        """Test creating repository with duplicate GitHub ID."""
        repo_data = {
            "github_id": test_repository.github_id,  # Duplicate
            "name": "duplicate-repo",
            "full_name": "testuser/duplicate-repo",
            "owner": "testuser",
        }

        response = client.post(
            "/api/repositories", json=repo_data, headers=auth_headers
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_repository_with_webhook(self, client, auth_headers):
        """Test creating repository with webhook ID."""
        repo_data = {
            "github_id": 88888,
            "name": "webhook-repo",
            "full_name": "testuser/webhook-repo",
            "owner": "testuser",
            "webhook_id": 12345,
        }

        response = client.post(
            "/api/repositories", json=repo_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["webhook_id"] == 12345

    def test_get_repository(self, client, auth_headers, test_repository):
        """Test getting a specific repository."""
        response = client.get(
            f"/api/repositories/{test_repository.id}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_repository.id)
        assert data["name"] == "test-repo"
        assert data["github_id"] == test_repository.github_id

    def test_get_repository_not_found(self, client, auth_headers):
        """Test getting non-existent repository."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/repositories/{fake_uuid}", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_repository_unauthorized_user(
        self, client, other_user, test_repository
    ):
        """Test getting repository owned by another user."""
        # Create token for other user
        token = create_user_token(
            user_id=str(other_user.id),
            github_id=other_user.github_id,
            username=other_user.username,
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/repositories/{test_repository.id}", headers=headers)

        assert response.status_code == 404  # Returns 404 to prevent info leak

    def test_update_repository(self, client, auth_headers, test_repository, db_session):
        """Test updating a repository."""
        update_data = {"name": "updated-repo", "is_active": False}

        response = client.patch(
            f"/api/repositories/{test_repository.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated-repo"
        assert data["is_active"] is False

        # Verify in database
        db_session.refresh(test_repository)
        assert test_repository.name == "updated-repo"
        assert test_repository.is_active is False

    def test_update_repository_partial(
        self, client, auth_headers, test_repository, db_session
    ):
        """Test partial update of repository."""
        original_name = test_repository.name
        update_data = {"is_active": False}

        response = client.patch(
            f"/api/repositories/{test_repository.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name  # Unchanged
        assert data["is_active"] is False  # Changed

    def test_update_repository_not_found(self, client, auth_headers):
        """Test updating non-existent repository."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        update_data = {"is_active": False}

        response = client.patch(
            f"/api/repositories/{fake_uuid}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_repository(self, client, auth_headers, test_repository, db_session):
        """Test deleting a repository."""
        repo_id = test_repository.id

        response = client.delete(
            f"/api/repositories/{repo_id}", headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deleted from database
        repo = db_session.query(Repository).filter(Repository.id == repo_id).first()
        assert repo is None

    def test_delete_repository_not_found(self, client, auth_headers):
        """Test deleting non-existent repository."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        response = client.delete(f"/api/repositories/{fake_uuid}", headers=auth_headers)

        assert response.status_code == 404

    def test_sync_repository(self, client, auth_headers, test_repository):
        """Test manual repository sync endpoint."""
        response = client.post(
            f"/api/repositories/{test_repository.id}/sync", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_repository.id)
        # In Sprint 1, this is just a placeholder that returns the repo

    def test_sync_repository_not_found(self, client, auth_headers):
        """Test syncing non-existent repository."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"

        response = client.post(
            f"/api/repositories/{fake_uuid}/sync", headers=auth_headers
        )

        assert response.status_code == 404
