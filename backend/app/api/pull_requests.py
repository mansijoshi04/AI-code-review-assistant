"""
Pull Request API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.schemas.pull_request import PullRequestResponse, PullRequestList
from app.services.github_service import github_service

router = APIRouter()


@router.get("/repositories/{repository_id}/pulls", response_model=PullRequestList)
async def list_pull_requests(
    repository_id: str,
    state: Optional[str] = Query(None, description="Filter by state (open, closed, merged, all)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PullRequestList:
    """
    List pull requests for a repository.

    Args:
        repository_id: Repository UUID
        state: Filter by state (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        PullRequestList: List of pull requests

    Raises:
        HTTPException: If repository not found or not authorized
    """
    # Verify repository exists and user owns it
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id, Repository.user_id == current_user.id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    # Build query
    query = db.query(PullRequest).filter(PullRequest.repository_id == repository_id)

    # Apply state filter if provided
    if state and state != "all":
        query = query.filter(PullRequest.state == state)

    # Get total count
    total = query.count()

    # Apply pagination
    pull_requests = query.order_by(PullRequest.updated_at.desc()).offset(skip).limit(limit).all()

    return PullRequestList(
        pull_requests=[
            PullRequestResponse.model_validate(pr) for pr in pull_requests
        ],
        total=total,
    )


@router.get("/pulls/{pull_request_id}", response_model=PullRequestResponse)
async def get_pull_request(
    pull_request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PullRequestResponse:
    """
    Get details of a specific pull request.

    Args:
        pull_request_id: Pull request UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        PullRequestResponse: Pull request data

    Raises:
        HTTPException: If pull request not found or not authorized
    """
    # Get pull request and verify access
    pull_request = (
        db.query(PullRequest)
        .join(Repository)
        .filter(
            PullRequest.id == pull_request_id,
            Repository.user_id == current_user.id,
        )
        .first()
    )

    if not pull_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pull request not found",
        )

    return PullRequestResponse.model_validate(pull_request)


@router.post("/repositories/{repository_id}/sync-pulls")
async def sync_repository_pulls(
    repository_id: str,
    state: str = Query("open", description="PR state to sync (open, closed, all)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Manually sync pull requests from GitHub for a repository.

    Fetches PRs from GitHub API and updates the database.

    Args:
        repository_id: Repository UUID
        state: PR state to sync (open, closed, all)
        current_user: Authenticated user
        db: Database session

    Returns:
        Dict with sync results

    Raises:
        HTTPException: If repository not found or not authorized
    """
    # Verify repository exists and user owns it
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id, Repository.user_id == current_user.id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    # Split owner and repo name
    owner, repo_name = repository.full_name.split("/")

    try:
        # Fetch PRs from GitHub
        github_prs = await github_service.get_pull_requests(
            access_token=current_user.access_token,
            owner=owner,
            repo=repo_name,
            state=state,
        )

        created_count = 0
        updated_count = 0

        # Process each PR
        for gh_pr in github_prs:
            # Check if PR exists in database
            pr = (
                db.query(PullRequest)
                .filter(
                    PullRequest.repository_id == repository_id,
                    PullRequest.pr_number == gh_pr["number"],
                )
                .first()
            )

            if pr:
                # Update existing PR
                pr.title = gh_pr["title"]
                pr.description = gh_pr.get("body")
                pr.state = gh_pr["state"]
                pr.author = gh_pr["user"]["login"]
                pr.base_branch = gh_pr["base"]["ref"]
                pr.head_branch = gh_pr["head"]["ref"]
                pr.files_changed = gh_pr.get("changed_files")
                pr.additions = gh_pr.get("additions")
                pr.deletions = gh_pr.get("deletions")
                pr.github_url = gh_pr["html_url"]
                updated_count += 1
            else:
                # Create new PR
                pr = PullRequest(
                    repository_id=repository_id,
                    pr_number=gh_pr["number"],
                    title=gh_pr["title"],
                    description=gh_pr.get("body"),
                    state=gh_pr["state"],
                    author=gh_pr["user"]["login"],
                    base_branch=gh_pr["base"]["ref"],
                    head_branch=gh_pr["head"]["ref"],
                    files_changed=gh_pr.get("changed_files"),
                    additions=gh_pr.get("additions"),
                    deletions=gh_pr.get("deletions"),
                    github_url=gh_pr["html_url"],
                )
                db.add(pr)
                created_count += 1

        db.commit()

        return {
            "status": "success",
            "message": f"Synced {len(github_prs)} pull requests",
            "created": created_count,
            "updated": updated_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync pull requests: {str(e)}",
        )
