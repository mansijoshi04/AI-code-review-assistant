"""
Unit tests for database models.
"""

import pytest
from datetime import datetime, date
from app.models.user import User
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review import Review
from app.models.finding import Finding
from app.models.review_metrics import ReviewMetrics


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, db_session):
        """Test creating a user."""
        user = User(
            github_id=12345,
            username="testuser",
            email="test@example.com",
            avatar_url="https://avatar.url",
            access_token="test_token",
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.github_id == 12345
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_to_dict(self, db_session):
        """Test user to_dict method."""
        user = User(
            github_id=12345,
            username="testuser",
            email="test@example.com",
        )
        db_session.add(user)
        db_session.commit()

        user_dict = user.to_dict()
        assert "id" in user_dict
        assert user_dict["github_id"] == 12345
        assert user_dict["username"] == "testuser"
        assert "access_token" not in user_dict  # Should not include sensitive data

    def test_user_unique_github_id(self, db_session):
        """Test that github_id is unique."""
        user1 = User(github_id=12345, username="user1")
        db_session.add(user1)
        db_session.commit()

        user2 = User(github_id=12345, username="user2")
        db_session.add(user2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()


class TestRepositoryModel:
    """Tests for Repository model."""

    def test_create_repository(self, db_session):
        """Test creating a repository."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
            is_active=True,
        )
        db_session.add(repo)
        db_session.commit()

        assert repo.id is not None
        assert repo.user_id == user.id
        assert repo.github_id == 67890
        assert repo.is_active is True

    def test_repository_user_relationship(self, db_session):
        """Test repository-user relationship."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        # Test forward relationship
        assert repo.user == user

        # Test backward relationship
        user_repos = user.repositories.all()
        assert len(user_repos) == 1
        assert user_repos[0] == repo

    def test_repository_cascade_delete(self, db_session):
        """Test that deleting a user cascades to repositories."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        repo_id = repo.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Repository should be deleted
        deleted_repo = db_session.query(Repository).filter(Repository.id == repo_id).first()
        assert deleted_repo is None


class TestPullRequestModel:
    """Tests for PullRequest model."""

    def test_create_pull_request(self, db_session):
        """Test creating a pull request."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr = PullRequest(
            repository_id=repo.id,
            pr_number=1,
            title="Test PR",
            description="Test description",
            author="testuser",
            state="open",
            base_branch="main",
            head_branch="feature",
            files_changed=5,
            additions=100,
            deletions=50,
        )
        db_session.add(pr)
        db_session.commit()

        assert pr.id is not None
        assert pr.pr_number == 1
        assert pr.title == "Test PR"
        assert pr.state == "open"

    def test_pull_request_unique_constraint(self, db_session):
        """Test unique constraint on (repository_id, pr_number)."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr1 = PullRequest(
            repository_id=repo.id,
            pr_number=1,
            title="Test PR 1",
        )
        db_session.add(pr1)
        db_session.commit()

        pr2 = PullRequest(
            repository_id=repo.id,
            pr_number=1,  # Same pr_number in same repo
            title="Test PR 2",
        )
        db_session.add(pr2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()


class TestReviewModel:
    """Tests for Review model."""

    def test_create_review(self, db_session):
        """Test creating a review."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr = PullRequest(
            repository_id=repo.id,
            pr_number=1,
            title="Test PR",
        )
        db_session.add(pr)
        db_session.commit()

        review = Review(
            pull_request_id=pr.id,
            status="completed",
            overall_score=85,
            summary="Good code quality",
            critical_count=0,
            warning_count=2,
            info_count=5,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db_session.add(review)
        db_session.commit()

        assert review.id is not None
        assert review.status == "completed"
        assert review.overall_score == 85
        assert review.critical_count == 0
        assert review.warning_count == 2
        assert review.info_count == 5

    def test_review_pull_request_relationship(self, db_session):
        """Test review-pull request relationship."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr = PullRequest(
            repository_id=repo.id,
            pr_number=1,
            title="Test PR",
        )
        db_session.add(pr)
        db_session.commit()

        review = Review(
            pull_request_id=pr.id,
            status="completed",
            overall_score=85,
        )
        db_session.add(review)
        db_session.commit()

        # Test forward relationship
        assert review.pull_request == pr

        # Test backward relationship
        pr_reviews = pr.reviews.all()
        assert len(pr_reviews) == 1
        assert pr_reviews[0] == review


class TestFindingModel:
    """Tests for Finding model."""

    def test_create_finding(self, db_session):
        """Test creating a finding."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr = PullRequest(
            repository_id=repo.id,
            pr_number=1,
            title="Test PR",
        )
        db_session.add(pr)
        db_session.commit()

        review = Review(
            pull_request_id=pr.id,
            status="completed",
            overall_score=85,
        )
        db_session.add(review)
        db_session.commit()

        finding = Finding(
            review_id=review.id,
            category="security",
            severity="critical",
            title="SQL Injection vulnerability",
            description="Potential SQL injection in user input",
            file_path="app/db.py",
            line_number=42,
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
            suggestion="Use parameterized queries",
            tool_source="bandit",
        )
        db_session.add(finding)
        db_session.commit()

        assert finding.id is not None
        assert finding.category == "security"
        assert finding.severity == "critical"
        assert finding.tool_source == "bandit"

    def test_finding_to_dict(self, db_session):
        """Test finding to_dict method."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        pr = PullRequest(repository_id=repo.id, pr_number=1, title="Test PR")
        db_session.add(pr)
        db_session.commit()

        review = Review(pull_request_id=pr.id, status="completed")
        db_session.add(review)
        db_session.commit()

        finding = Finding(
            review_id=review.id,
            category="security",
            severity="critical",
            title="Test finding",
        )
        db_session.add(finding)
        db_session.commit()

        finding_dict = finding.to_dict()
        assert "id" in finding_dict
        assert finding_dict["category"] == "security"
        assert finding_dict["severity"] == "critical"


class TestReviewMetricsModel:
    """Tests for ReviewMetrics model."""

    def test_create_review_metrics(self, db_session):
        """Test creating review metrics."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        metrics = ReviewMetrics(
            repository_id=repo.id,
            date=date.today(),
            total_reviews=10,
            avg_score=85.5,
            total_findings=25,
            critical_findings=2,
            avg_review_time_seconds=120,
        )
        db_session.add(metrics)
        db_session.commit()

        assert metrics.id is not None
        assert metrics.total_reviews == 10
        assert float(metrics.avg_score) == 85.5
        assert metrics.critical_findings == 2

    def test_review_metrics_unique_constraint(self, db_session):
        """Test unique constraint on (repository_id, date)."""
        user = User(github_id=12345, username="testuser")
        db_session.add(user)
        db_session.commit()

        repo = Repository(
            user_id=user.id,
            github_id=67890,
            name="test-repo",
            full_name="testuser/test-repo",
            owner="testuser",
        )
        db_session.add(repo)
        db_session.commit()

        today = date.today()

        metrics1 = ReviewMetrics(
            repository_id=repo.id,
            date=today,
            total_reviews=10,
        )
        db_session.add(metrics1)
        db_session.commit()

        metrics2 = ReviewMetrics(
            repository_id=repo.id,
            date=today,  # Same date for same repo
            total_reviews=20,
        )
        db_session.add(metrics2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
