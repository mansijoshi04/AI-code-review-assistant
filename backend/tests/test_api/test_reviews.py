"""
Integration tests for review API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review import Review
from app.models.finding import Finding


@pytest.fixture
def test_repository(db_session, test_user):
    """Create a test repository."""
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
    return repo


@pytest.fixture
def test_pull_request(db_session, test_repository):
    """Create a test pull request."""
    pr = PullRequest(
        repository_id=test_repository.id,
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
    return pr


@pytest.fixture
def test_review(db_session, test_pull_request):
    """Create a test review."""
    review = Review(
        pull_request_id=test_pull_request.id,
        status="completed",
        critical_count=2,
        warning_count=5,
        info_count=10,
        overall_score=60,
        summary="Test review summary",
    )
    db_session.add(review)
    db_session.commit()
    db_session.refresh(review)
    return review


@pytest.fixture
def test_findings(db_session, test_review):
    """Create test findings."""
    findings = []

    # Critical finding
    finding1 = Finding(
        review_id=test_review.id,
        category="security",
        severity="critical",
        title="SQL Injection Risk",
        description="Potential SQL injection vulnerability",
        file_path="app/db.py",
        line_number=42,
        code_snippet="query = 'SELECT * FROM users WHERE id = ' + user_id",
        suggestion="Use parameterized queries",
        tool_source="bandit",
    )
    findings.append(finding1)

    # Warning finding
    finding2 = Finding(
        review_id=test_review.id,
        category="quality",
        severity="warning",
        title="Unused variable",
        description="Variable 'x' is defined but never used",
        file_path="app/utils.py",
        line_number=15,
        code_snippet="x = 10",
        suggestion="Remove unused variable",
        tool_source="pylint",
    )
    findings.append(finding2)

    # Info finding
    finding3 = Finding(
        review_id=test_review.id,
        category="complexity",
        severity="info",
        title="Function complexity",
        description="Function has moderate complexity",
        file_path="app/service.py",
        line_number=100,
        suggestion="Consider breaking down into smaller functions",
        tool_source="radon",
    )
    findings.append(finding3)

    for finding in findings:
        db_session.add(finding)

    db_session.commit()

    for finding in findings:
        db_session.refresh(finding)

    return findings


class TestReviewEndpoints:
    """Tests for review API endpoints."""

    @patch("app.services.review_service.review_service._run_analysis")
    def test_create_review(
        self, mock_analysis, client, auth_headers, test_pull_request
    ):
        """Test creating a new code review."""
        # Mock the async analysis so it doesn't actually run
        mock_analysis.return_value = None

        response = client.post(
            f"/api/pulls/{test_pull_request.id}/reviews",
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["pull_request_id"] == str(test_pull_request.id)
        assert data["status"] == "pending"
        assert data["critical_count"] == 0
        assert data["warning_count"] == 0
        assert data["info_count"] == 0

    def test_create_review_pr_not_found(self, client, auth_headers):
        """Test creating review for non-existent PR."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/pulls/{fake_uuid}/reviews",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_review_unauthorized(
        self, client, other_user, test_pull_request
    ):
        """Test creating review for PR owned by another user."""
        from app.core.security import create_user_token

        # Create token for other user
        token = create_user_token(
            user_id=str(other_user.id),
            github_id=other_user.github_id,
            username=other_user.username,
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/api/pulls/{test_pull_request.id}/reviews",
            headers=headers,
        )

        assert response.status_code == 404

    def test_list_reviews_empty(self, client, auth_headers, test_user):
        """Test listing reviews when there are none."""
        response = client.get("/api/reviews", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["reviews"] == []

    def test_list_reviews(self, client, auth_headers, test_review):
        """Test listing all reviews."""
        response = client.get("/api/reviews", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["reviews"]) == 1
        assert data["reviews"][0]["id"] == str(test_review.id)
        assert data["reviews"][0]["status"] == "completed"
        assert data["reviews"][0]["overall_score"] == 60

    def test_list_reviews_with_status_filter(
        self, client, auth_headers, test_review, db_session, test_pull_request
    ):
        """Test filtering reviews by status."""
        # Create a pending review
        pending_review = Review(
            pull_request_id=test_pull_request.id,
            status="pending",
            critical_count=0,
            warning_count=0,
            info_count=0,
        )
        db_session.add(pending_review)
        db_session.commit()

        # Filter for completed reviews
        response = client.get(
            "/api/reviews",
            params={"status_filter": "completed"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["reviews"][0]["status"] == "completed"

        # Filter for pending reviews
        response = client.get(
            "/api/reviews",
            params={"status_filter": "pending"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["reviews"][0]["status"] == "pending"

    def test_list_reviews_pagination(
        self, client, auth_headers, test_review, db_session, test_pull_request
    ):
        """Test review listing with pagination."""
        # Create additional reviews
        for i in range(5):
            review = Review(
                pull_request_id=test_pull_request.id,
                status="completed",
                critical_count=i,
                warning_count=i * 2,
                info_count=i * 3,
                overall_score=80 - i * 5,
            )
            db_session.add(review)
        db_session.commit()

        # Test with limit
        response = client.get(
            "/api/reviews",
            params={"limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6  # 1 from fixture + 5 new
        assert len(data["reviews"]) == 3

        # Test with skip
        response = client.get(
            "/api/reviews",
            params={"skip": 2, "limit": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6
        assert len(data["reviews"]) == 2

    def test_get_review(self, client, auth_headers, test_review):
        """Test getting a specific review."""
        response = client.get(
            f"/api/reviews/{test_review.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_review.id)
        assert data["status"] == "completed"
        assert data["critical_count"] == 2
        assert data["warning_count"] == 5
        assert data["info_count"] == 10
        assert data["overall_score"] == 60

    def test_get_review_not_found(self, client, auth_headers):
        """Test getting non-existent review."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/reviews/{fake_uuid}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_review_unauthorized(self, client, other_user, test_review):
        """Test getting review owned by another user."""
        from app.core.security import create_user_token

        # Create token for other user
        token = create_user_token(
            user_id=str(other_user.id),
            github_id=other_user.github_id,
            username=other_user.username,
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            f"/api/reviews/{test_review.id}",
            headers=headers,
        )

        assert response.status_code == 404

    def test_list_review_findings(
        self, client, auth_headers, test_review, test_findings
    ):
        """Test listing findings for a review."""
        response = client.get(
            f"/api/reviews/{test_review.id}/findings",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["findings"]) == 3
        assert data["critical_count"] == 1
        assert data["warning_count"] == 1
        assert data["info_count"] == 1

    def test_list_findings_filter_by_severity(
        self, client, auth_headers, test_review, test_findings
    ):
        """Test filtering findings by severity."""
        response = client.get(
            f"/api/reviews/{test_review.id}/findings",
            params={"severity": "critical"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["findings"]) == 1
        assert data["findings"][0]["severity"] == "critical"
        assert data["findings"][0]["category"] == "security"

    def test_list_findings_filter_by_category(
        self, client, auth_headers, test_review, test_findings
    ):
        """Test filtering findings by category."""
        response = client.get(
            f"/api/reviews/{test_review.id}/findings",
            params={"category": "quality"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["findings"]) == 1
        assert data["findings"][0]["category"] == "quality"
        assert data["findings"][0]["severity"] == "warning"

    def test_list_findings_pagination(
        self, client, auth_headers, test_review, test_findings, db_session
    ):
        """Test finding listing with pagination."""
        # Create additional findings
        for i in range(10):
            finding = Finding(
                review_id=test_review.id,
                category="quality",
                severity="info",
                title=f"Finding {i}",
                description=f"Description {i}",
            )
            db_session.add(finding)
        db_session.commit()

        # Test with limit
        response = client.get(
            f"/api/reviews/{test_review.id}/findings",
            params={"limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 13  # 3 from fixture + 10 new
        assert len(data["findings"]) == 5

    def test_list_findings_review_not_found(self, client, auth_headers):
        """Test listing findings for non-existent review."""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/reviews/{fake_uuid}/findings",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_review_stats_empty(self, client, auth_headers, test_user):
        """Test getting review statistics when there are no reviews."""
        response = client.get("/api/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_reviews"] == 0
        assert data["pending_reviews"] == 0
        assert data["completed_reviews"] == 0
        assert data["failed_reviews"] == 0
        assert data["avg_score"] is None
        assert data["total_critical_findings"] == 0
        assert data["total_warning_findings"] == 0
        assert data["total_info_findings"] == 0

    def test_get_review_stats(
        self, client, auth_headers, test_review, db_session, test_pull_request
    ):
        """Test getting review statistics."""
        # Create additional reviews with different statuses
        pending_review = Review(
            pull_request_id=test_pull_request.id,
            status="pending",
            critical_count=0,
            warning_count=0,
            info_count=0,
        )
        db_session.add(pending_review)

        failed_review = Review(
            pull_request_id=test_pull_request.id,
            status="failed",
            critical_count=0,
            warning_count=0,
            info_count=0,
        )
        db_session.add(failed_review)

        completed_review2 = Review(
            pull_request_id=test_pull_request.id,
            status="completed",
            critical_count=1,
            warning_count=3,
            info_count=5,
            overall_score=80,
        )
        db_session.add(completed_review2)

        db_session.commit()

        response = client.get("/api/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_reviews"] == 4
        assert data["pending_reviews"] == 1
        assert data["completed_reviews"] == 2
        assert data["failed_reviews"] == 1
        assert data["avg_score"] == 70  # (60 + 80) / 2
        assert data["total_critical_findings"] == 3  # 2 + 1
        assert data["total_warning_findings"] == 8  # 5 + 3
        assert data["total_info_findings"] == 15  # 10 + 5
