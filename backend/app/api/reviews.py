"""
Review API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.models.pull_request import PullRequest
from app.models.review import Review
from app.models.finding import Finding
from app.schemas.review import ReviewResponse, ReviewList, ReviewCreate, ReviewStats
from app.schemas.finding import FindingResponse, FindingList
from app.services.review_service import review_service

router = APIRouter()


@router.post("/pulls/{pull_request_id}/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(
    pull_request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """
    Create and trigger a new code review for a pull request.

    Args:
        pull_request_id: Pull request UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        ReviewResponse: Created review data

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

    # Create and run review
    review = await review_service.create_review(pull_request, current_user, db)

    return ReviewResponse.model_validate(review)


@router.get("/reviews", response_model=ReviewList)
async def list_reviews(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewList:
    """
    List all reviews for current user's pull requests.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by review status
        current_user: Authenticated user
        db: Database session

    Returns:
        ReviewList: List of reviews
    """
    # Build query
    query = (
        db.query(Review)
        .join(PullRequest)
        .join(Repository)
        .filter(Repository.user_id == current_user.id)
    )

    # Apply status filter if provided
    if status_filter:
        query = query.filter(Review.status == status_filter)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    reviews = query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

    return ReviewList(
        reviews=[ReviewResponse.model_validate(r) for r in reviews],
        total=total,
    )


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewResponse:
    """
    Get details of a specific review.

    Args:
        review_id: Review UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        ReviewResponse: Review data

    Raises:
        HTTPException: If review not found or not authorized
    """
    # Get review and verify access
    review = (
        db.query(Review)
        .join(PullRequest)
        .join(Repository)
        .filter(
            Review.id == review_id,
            Repository.user_id == current_user.id,
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return ReviewResponse.model_validate(review)


@router.get("/reviews/{review_id}/findings", response_model=FindingList)
async def list_review_findings(
    review_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FindingList:
    """
    List findings for a specific review.

    Args:
        review_id: Review UUID
        severity: Filter by severity (optional)
        category: Filter by category (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session

    Returns:
        FindingList: List of findings with counts

    Raises:
        HTTPException: If review not found or not authorized
    """
    # Verify review exists and user has access
    review = (
        db.query(Review)
        .join(PullRequest)
        .join(Repository)
        .filter(
            Review.id == review_id,
            Repository.user_id == current_user.id,
        )
        .first()
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    # Build query
    query = db.query(Finding).filter(Finding.review_id == review_id)

    # Apply filters
    if severity:
        query = query.filter(Finding.severity == severity)
    if category:
        query = query.filter(Finding.category == category)

    # Get total and counts
    total = query.count()
    critical_count = db.query(Finding).filter(
        Finding.review_id == review_id, Finding.severity == "critical"
    ).count()
    warning_count = db.query(Finding).filter(
        Finding.review_id == review_id, Finding.severity == "warning"
    ).count()
    info_count = db.query(Finding).filter(
        Finding.review_id == review_id, Finding.severity == "info"
    ).count()

    # Apply pagination
    findings = query.offset(skip).limit(limit).all()

    return FindingList(
        findings=[FindingResponse.model_validate(f) for f in findings],
        total=total,
        critical_count=critical_count,
        warning_count=warning_count,
        info_count=info_count,
    )


@router.get("/stats", response_model=ReviewStats)
async def get_review_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReviewStats:
    """
    Get review statistics for current user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        ReviewStats: Review statistics
    """
    # Get all reviews for user's repos
    reviews = (
        db.query(Review)
        .join(PullRequest)
        .join(Repository)
        .filter(Repository.user_id == current_user.id)
        .all()
    )

    total_reviews = len(reviews)
    pending_reviews = sum(1 for r in reviews if r.status == "pending")
    completed_reviews = sum(1 for r in reviews if r.status == "completed")
    failed_reviews = sum(1 for r in reviews if r.status == "failed")

    # Calculate average score (only completed reviews)
    completed_with_scores = [r for r in reviews if r.status == "completed" and r.overall_score is not None]
    avg_score = (
        sum(r.overall_score for r in completed_with_scores) / len(completed_with_scores)
        if completed_with_scores
        else None
    )

    # Count total findings
    total_critical = sum(r.critical_count for r in reviews)
    total_warnings = sum(r.warning_count for r in reviews)
    total_info = sum(r.info_count for r in reviews)

    return ReviewStats(
        total_reviews=total_reviews,
        pending_reviews=pending_reviews,
        completed_reviews=completed_reviews,
        failed_reviews=failed_reviews,
        avg_score=avg_score,
        total_critical_findings=total_critical,
        total_warning_findings=total_warnings,
        total_info_findings=total_info,
    )
