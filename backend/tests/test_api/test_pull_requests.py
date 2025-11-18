"""
Integration tests for pull request API endpoints.
"""

import pytest
from app.models.repository import Repository
from app.models.pull_request import PullRequest


@pytest.fixture
def test_pull_request(db_session, test_user):
    """Create a test repository and pull request."""
    repo = Repository(
        user_id=test_user.id,
        github_id=99999,
        name="test-repo",
        full_name="testuser/test-repo",
        owner="testuser",
    )
    db_session.add(repo)
    db_session.commit()
    db_session.refresh(repo)

    pr = PullRequest(
        repository_id=repo.id,
        pr_number=1,
        title="Test Pull Request",
        description="This is a test PR",
        author="testuser",
        state="open",
        base_branch="main",
        head_branch="feature-branch",
        files_changed=5,
        additions=100,
        deletions=50,
        github_url="https://github.com/testuser/test-repo/pull/1",
    )
    db_session.add(pr)
    db_session.commit()
    db_session.refresh(pr)

    return {"repository": repo, "pull_request": pr}


class TestPullRequestEndpoints:
    """Tests for pull request API endpoints."""

    def test_list_pull_requests_empty(self, client, auth_headers, test_user, db_session):
        """Test listing pull requests when repository has none."""
        # Create repository without PRs
        repo = Repository(
            user_id=test_user.id,
            github_id=88888,
            name="empty-repo",
            full_name="testuser/empty-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        response = client.get(
            f"/api/repositories/{repo.id}/pulls", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["pull_requests"] == []

    def test_list_pull_requests(self, client, auth_headers, test_pull_request):
        """Test listing pull requests."""
        repo = test_pull_request["repository"]

        response = client.get(
            f"/api/repositories/{repo.id}/pulls", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["pull_requests"]) == 1
        assert data["pull_requests"][0]["pr_number"] == 1
        assert data["pull_requests"][0]["title"] == "Test Pull Request"

    def test_list_pull_requests_filter_by_state(
        self, client, auth_headers, test_pull_request, db_session
    ):
        """Test filtering pull requests by state."""
        repo = test_pull_request["repository"]

        # Create a closed PR
        closed_pr = PullRequest(
            repository_id=repo.id,
            pr_number=2,
            title="Closed PR",
            state="closed",
        )
        db_session.add(closed_pr)
        db_session.commit()

        # Filter for open PRs
        response = client.get(
            f"/api/repositories/{repo.id}/pulls",
            params={"state": "open"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["pull_requests"][0]["state"] == "open"

        # Filter for closed PRs
        response = client.get(
            f"/api/repositories/{repo.id}/pulls",
            params={"state": "closed"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["pull_requests"][0]["state"] == "closed"

    def test_list_pull_requests_pagination(
        self, client, auth_headers, test_pull_request, db_session
    ):
        """Test pull request listing with pagination."""
        repo = test_pull_request["repository"]

        # Create multiple PRs
        for i in range(5):
            pr = PullRequest(
                repository_id=repo.id,
                pr_number=i + 10,
                title=f"PR #{i + 10}",
                state="open",
            )
            db_session.add(pr)
        db_session.commit()

        # Test with limit
        response = client.get(
            f"/api/repositories/{repo.id}/pulls",
            params={"limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6  # 1 from fixture + 5 new
        assert len(data["pull_requests"]) == 3

        # Test with skip
        response = client.get(
            f"/api/repositories/{repo.id}/pulls",
            params={"skip": 2, "limit": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert len(data["pull_requests"]) == 2

    def test_list_pull_requests_unauthorized(self, client, other_user, test_pull_request):
        """Test listing pull requests for repository owned by another user."""
        from app.core.security import create_user_token

        repo = test_pull_request["repository"]

        # Create token for other user
        token = create_user_token(
            user_id=str(other_user.id),
            github_id=other_user.github_id,
            username=other_user.username,
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/repositories/{repo.id}/pulls", headers=headers)

        assert response.status_code == 404

    def test_get_pull_request(self, client, auth_headers, test_pull_request):
        """Test getting a specific pull request."""
        pr = test_pull_request["pull_request"]

        response = client.get(f"/api/pulls/{pr.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(pr.id)
        assert data["pr_number"] == 1
        assert data["title"] == "Test Pull Request"
        assert data["state"] == "open"

    def test_get_pull_request_not_found(self, client, auth_headers):
        """Test getting non-existent pull request."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/pulls/{fake_uuid}", headers=auth_headers)

        assert response.status_code == 404

    def test_get_pull_request_unauthorized(
        self, client, other_user, test_pull_request
    ):
        """Test getting pull request owned by another user."""
        from app.core.security import create_user_token

        pr = test_pull_request["pull_request"]

        # Create token for other user
        token = create_user_token(
            user_id=str(other_user.id),
            github_id=other_user.github_id,
            username=other_user.username,
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/pulls/{pr.id}", headers=headers)

        assert response.status_code == 404
