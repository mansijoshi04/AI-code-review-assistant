"""
Repository API endpoints for managing GitHub repositories.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.repository import Repository
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryResponse,
    RepositoryList,
)

router = APIRouter()


@router.get("", response_model=RepositoryList)
async def list_repositories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    is_active: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryList:
    """
    List repositories for the current user.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status (optional)
        current_user: Authenticated user
        db: Database session

    Returns:
        RepositoryList: List of repositories and total count
    """
    query = db.query(Repository).filter(Repository.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(Repository.is_active == is_active)

    total = query.count()
    repositories = query.offset(skip).limit(limit).all()

    return RepositoryList(
        repositories=[RepositoryResponse.model_validate(r) for r in repositories],
        total=total,
    )


@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
    repository: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """
    Create a new repository.

    Args:
        repository: Repository data
        current_user: Authenticated user
        db: Database session

    Returns:
        RepositoryResponse: Created repository

    Raises:
        HTTPException: If repository with same github_id already exists
    """
    # Check if repository already exists
    existing = (
        db.query(Repository)
        .filter(Repository.github_id == repository.github_id)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Repository with this GitHub ID already exists",
        )

    # Create new repository
    db_repository = Repository(
        user_id=current_user.id,
        github_id=repository.github_id,
        name=repository.name,
        full_name=repository.full_name,
        owner=repository.owner,
        is_active=repository.is_active,
        webhook_id=repository.webhook_id,
    )

    db.add(db_repository)
    db.commit()
    db.refresh(db_repository)

    return RepositoryResponse.model_validate(db_repository)


@router.get("/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """
    Get a specific repository by ID.

    Args:
        repository_id: Repository UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        RepositoryResponse: Repository data

    Raises:
        HTTPException: If repository not found or not authorized
    """
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

    return RepositoryResponse.model_validate(repository)


@router.patch("/{repository_id}", response_model=RepositoryResponse)
async def update_repository(
    repository_id: str,
    repository_update: RepositoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """
    Update a repository.

    Args:
        repository_id: Repository UUID
        repository_update: Fields to update
        current_user: Authenticated user
        db: Database session

    Returns:
        RepositoryResponse: Updated repository

    Raises:
        HTTPException: If repository not found or not authorized
    """
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

    # Update fields
    update_data = repository_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(repository, field, value)

    db.commit()
    db.refresh(repository)

    return RepositoryResponse.model_validate(repository)


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a repository.

    Args:
        repository_id: Repository UUID
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException: If repository not found or not authorized
    """
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

    db.delete(repository)
    db.commit()


@router.post("/{repository_id}/sync", response_model=RepositoryResponse)
async def sync_repository(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryResponse:
    """
    Manually sync a repository with GitHub.
    (Placeholder for Sprint 2 GitHub integration)

    Args:
        repository_id: Repository UUID
        current_user: Authenticated user
        db: Database session

    Returns:
        RepositoryResponse: Repository data

    Raises:
        HTTPException: If repository not found or not authorized
    """
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

    # TODO: Implement GitHub sync in Sprint 2
    # For now, just return the repository

    return RepositoryResponse.model_validate(repository)
