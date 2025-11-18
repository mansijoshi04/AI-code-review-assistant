"""
Pull request service for processing GitHub PR events.
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.schemas.webhook import PullRequestWebhookPayload
from app.services.github_service import github_service


class PullRequestService:
    """Service for processing pull request events from webhooks."""

    async def process_pr_opened(
        self, webhook_data: PullRequestWebhookPayload, db: Session
    ) -> PullRequest:
        """
        Process pull_request opened event.

        Creates or updates the PR record in database and triggers review.

        Args:
            webhook_data: Validated webhook payload
            db: Database session

        Returns:
            PullRequest: Created/updated pull request model
        """
        # Find repository in database
        repository = (
            db.query(Repository)
            .filter(Repository.github_id == webhook_data.repository.id)
            .first()
        )

        if not repository:
            # Repository not being monitored, skip processing
            print(
                f"Repository {webhook_data.repository.full_name} not found in database"
            )
            return None

        # Check if PR already exists
        pull_request = (
            db.query(PullRequest)
            .filter(
                PullRequest.repository_id == repository.id,
                PullRequest.pr_number == webhook_data.number,
            )
            .first()
        )

        pr_data = webhook_data.pull_request

        if pull_request:
            # Update existing PR
            pull_request.title = pr_data.title
            pull_request.description = pr_data.body
            pull_request.author = pr_data.user.get("login")
            pull_request.state = pr_data.state
            pull_request.base_branch = pr_data.base.get("ref")
            pull_request.head_branch = pr_data.head.get("ref")
            pull_request.files_changed = pr_data.changed_files
            pull_request.additions = pr_data.additions
            pull_request.deletions = pr_data.deletions
            pull_request.github_url = pr_data.html_url
        else:
            # Create new PR
            pull_request = PullRequest(
                repository_id=repository.id,
                pr_number=webhook_data.number,
                title=pr_data.title,
                description=pr_data.body,
                author=pr_data.user.get("login"),
                state=pr_data.state,
                base_branch=pr_data.base.get("ref"),
                head_branch=pr_data.head.get("ref"),
                files_changed=pr_data.changed_files,
                additions=pr_data.additions,
                deletions=pr_data.deletions,
                github_url=pr_data.html_url,
            )
            db.add(pull_request)

        db.commit()
        db.refresh(pull_request)

        # TODO: In Sprint 3, trigger automatic code review here
        print(
            f"PR #{pull_request.pr_number} stored. Review will be triggered in Sprint 3."
        )

        return pull_request

    async def process_pr_updated(
        self, webhook_data: PullRequestWebhookPayload, db: Session
    ) -> PullRequest:
        """
        Process pull_request synchronize event.

        Updates PR record and triggers new review for new commits.

        Args:
            webhook_data: Validated webhook payload
            db: Database session

        Returns:
            PullRequest: Updated pull request model
        """
        # Find repository
        repository = (
            db.query(Repository)
            .filter(Repository.github_id == webhook_data.repository.id)
            .first()
        )

        if not repository:
            print(
                f"Repository {webhook_data.repository.full_name} not found in database"
            )
            return None

        # Find PR
        pull_request = (
            db.query(PullRequest)
            .filter(
                PullRequest.repository_id == repository.id,
                PullRequest.pr_number == webhook_data.number,
            )
            .first()
        )

        if not pull_request:
            # PR doesn't exist, create it
            return await self.process_pr_opened(webhook_data, db)

        # Update PR with latest data
        pr_data = webhook_data.pull_request
        pull_request.title = pr_data.title
        pull_request.description = pr_data.body
        pull_request.state = pr_data.state
        pull_request.files_changed = pr_data.changed_files
        pull_request.additions = pr_data.additions
        pull_request.deletions = pr_data.deletions

        db.commit()
        db.refresh(pull_request)

        # TODO: In Sprint 3, trigger new code review for updated PR
        print(
            f"PR #{pull_request.pr_number} updated. New review will be triggered in Sprint 3."
        )

        return pull_request

    async def process_pr_closed(
        self, webhook_data: PullRequestWebhookPayload, db: Session
    ) -> PullRequest:
        """
        Process pull_request closed event.

        Updates PR state to closed or merged.

        Args:
            webhook_data: Validated webhook payload
            db: Database session

        Returns:
            PullRequest: Updated pull request model
        """
        # Find repository
        repository = (
            db.query(Repository)
            .filter(Repository.github_id == webhook_data.repository.id)
            .first()
        )

        if not repository:
            print(
                f"Repository {webhook_data.repository.full_name} not found in database"
            )
            return None

        # Find PR
        pull_request = (
            db.query(PullRequest)
            .filter(
                PullRequest.repository_id == repository.id,
                PullRequest.pr_number == webhook_data.number,
            )
            .first()
        )

        if not pull_request:
            # PR doesn't exist, create it as closed
            return await self.process_pr_opened(webhook_data, db)

        # Update PR state
        pr_data = webhook_data.pull_request
        if pr_data.merged_at:
            pull_request.state = "merged"
        else:
            pull_request.state = "closed"

        db.commit()
        db.refresh(pull_request)

        print(f"PR #{pull_request.pr_number} marked as {pull_request.state}")

        return pull_request

    async def get_pr_diff(
        self, repository: Repository, pr_number: int, user: User
    ) -> str:
        """
        Fetch PR diff from GitHub.

        Args:
            repository: Repository model
            pr_number: Pull request number
            user: User model (for access token)

        Returns:
            Diff content as string
        """
        owner, repo_name = repository.full_name.split("/")

        diff = await github_service.get_pull_request_diff(
            access_token=user.access_token,
            owner=owner,
            repo=repo_name,
            pull_number=pr_number,
        )

        return diff

    async def get_pr_files(
        self, repository: Repository, pr_number: int, user: User
    ) -> list:
        """
        Fetch list of files changed in PR from GitHub.

        Args:
            repository: Repository model
            pr_number: Pull request number
            user: User model (for access token)

        Returns:
            List of file change dictionaries
        """
        owner, repo_name = repository.full_name.split("/")

        files = await github_service.get_pull_request_files(
            access_token=user.access_token,
            owner=owner,
            repo=repo_name,
            pull_number=pr_number,
        )

        return files


# Global pull request service instance
pull_request_service = PullRequestService()
