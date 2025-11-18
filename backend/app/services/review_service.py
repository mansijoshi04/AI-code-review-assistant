"""
Review service for orchestrating code analysis.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.review import Review
from app.models.finding import Finding
from app.models.pull_request import PullRequest
from app.models.user import User
from app.services.github_service import github_service
from app.services.pull_request_service import pull_request_service
from app.services.analysis.base import (
    create_temp_workspace,
    cleanup_workspace,
    write_files_to_workspace,
    extract_python_files_from_diff,
)
from app.services.analysis.security import security_analyzer
from app.services.analysis.quality import quality_analyzer
from app.services.analysis.complexity import complexity_analyzer


class ReviewService:
    """Service for orchestrating code review process."""

    async def create_review(
        self, pull_request: PullRequest, user: User, db: Session
    ) -> Review:
        """
        Create and run a code review for a pull request.

        Args:
            pull_request: PullRequest model
            user: User model (for GitHub access token)
            db: Database session

        Returns:
            Review: Created review model
        """
        # Create review record
        review = Review(
            pull_request_id=pull_request.id,
            status="pending",
            critical_count=0,
            warning_count=0,
            info_count=0,
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        # Run analysis asynchronously (don't await - let it run in background)
        asyncio.create_task(self._run_analysis(review, pull_request, user, db))

        return review

    async def _run_analysis(
        self, review: Review, pull_request: PullRequest, user: User, db: Session
    ):
        """
        Run analysis pipeline in background.

        Args:
            review: Review model
            pull_request: PullRequest model
            user: User model
            db: Database session
        """
        workspace = None

        try:
            # Update status to in_progress
            review.status = "in_progress"
            review.started_at = datetime.utcnow()
            db.commit()

            # Get repository
            repository = pull_request.repository

            # Fetch PR diff from GitHub
            diff = await pull_request_service.get_pr_diff(
                repository, pull_request.pr_number, user
            )

            # Extract Python files from diff
            python_files = extract_python_files_from_diff(diff)

            if not python_files:
                # No Python files to analyze
                review.status = "completed"
                review.completed_at = datetime.utcnow()
                review.summary = "No Python files found in this pull request."
                review.overall_score = 100
                db.commit()
                return

            # Create temporary workspace
            workspace = create_temp_workspace()
            write_files_to_workspace(python_files, workspace)

            # Run analyzers in parallel
            results = await asyncio.gather(
                security_analyzer.analyze(python_files, workspace),
                quality_analyzer.analyze(python_files, workspace),
                complexity_analyzer.analyze(python_files, workspace),
                return_exceptions=True,
            )

            # Process results
            all_findings = []
            for result in results:
                if isinstance(result, Exception):
                    print(f"Analyzer error: {str(result)}")
                    continue

                if result.success:
                    all_findings.extend(result.findings)

            # Store findings in database
            critical_count = 0
            warning_count = 0
            info_count = 0

            for finding_data in all_findings:
                finding = Finding(
                    review_id=review.id,
                    category=finding_data.get("category", "unknown"),
                    severity=finding_data.get("severity", "info"),
                    title=finding_data.get("title", ""),
                    description=finding_data.get("description"),
                    file_path=finding_data.get("file_path"),
                    line_number=finding_data.get("line_number"),
                    code_snippet=finding_data.get("code_snippet"),
                    suggestion=finding_data.get("suggestion"),
                    tool_source=finding_data.get("tool_source"),
                )
                db.add(finding)

                # Count by severity
                if finding.severity == "critical":
                    critical_count += 1
                elif finding.severity == "warning":
                    warning_count += 1
                else:
                    info_count += 1

            # Calculate overall score
            overall_score = self._calculate_score(
                critical_count, warning_count, info_count
            )

            # Generate summary
            summary = self._generate_summary(
                critical_count, warning_count, info_count, all_findings
            )

            # Update review
            review.status = "completed"
            review.completed_at = datetime.utcnow()
            review.overall_score = overall_score
            review.critical_count = critical_count
            review.warning_count = warning_count
            review.info_count = info_count
            review.summary = summary

            db.commit()

        except Exception as e:
            # Mark review as failed
            review.status = "failed"
            review.completed_at = datetime.utcnow()
            review.summary = f"Review failed: {str(e)}"
            db.commit()
            print(f"Review failed: {str(e)}")

        finally:
            # Cleanup workspace
            if workspace:
                cleanup_workspace(workspace)

    def _calculate_score(
        self, critical_count: int, warning_count: int, info_count: int
    ) -> int:
        """
        Calculate overall review score (0-100).

        Score calculation:
        - Start at 100
        - Subtract 20 for each critical issue
        - Subtract 10 for each warning
        - Subtract 2 for each info

        Args:
            critical_count: Number of critical findings
            warning_count: Number of warning findings
            info_count: Number of info findings

        Returns:
            int: Score between 0 and 100
        """
        score = 100
        score -= critical_count * 20
        score -= warning_count * 10
        score -= info_count * 2

        # Clamp to 0-100
        return max(0, min(100, score))

    def _generate_summary(
        self,
        critical_count: int,
        warning_count: int,
        info_count: int,
        findings: List[Dict[str, Any]],
    ) -> str:
        """
        Generate summary text for the review.

        Args:
            critical_count: Number of critical findings
            warning_count: Number of warning findings
            info_count: Number of info findings
            findings: List of all findings

        Returns:
            str: Summary text
        """
        total = critical_count + warning_count + info_count

        if total == 0:
            return "Great work! No issues found in this pull request."

        summary_parts = [
            f"Found {total} issue(s) in this pull request:",
            f"- {critical_count} critical",
            f"- {warning_count} warnings",
            f"- {info_count} info",
        ]

        # Add category breakdown
        categories = {}
        for finding in findings:
            category = finding.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        if categories:
            summary_parts.append("\nIssues by category:")
            for category, count in sorted(
                categories.items(), key=lambda x: x[1], reverse=True
            ):
                summary_parts.append(f"- {category}: {count}")

        # Add recommendation
        if critical_count > 0:
            summary_parts.append(
                "\n⚠️ Critical issues found. Please address before merging."
            )
        elif warning_count > 5:
            summary_parts.append(
                "\n⚡ Several warnings found. Consider addressing them."
            )
        else:
            summary_parts.append("\n✓ Code looks good overall. Minor improvements suggested.")

        return "\n".join(summary_parts)


# Global review service instance
review_service = ReviewService()
