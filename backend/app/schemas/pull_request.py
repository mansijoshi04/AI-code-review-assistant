"""
Pydantic schemas for PullRequest model.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class PullRequestBase(BaseModel):
    """Base PullRequest schema with common fields."""

    pr_number: int = Field(..., gt=0)
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    author: Optional[str] = None
    state: Optional[str] = None  # open, closed, merged


class PullRequestCreate(PullRequestBase):
    """Schema for creating a new pull request."""

    repository_id: str
    base_branch: Optional[str] = None
    head_branch: Optional[str] = None
    files_changed: Optional[int] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    github_url: Optional[str] = None


class PullRequestUpdate(BaseModel):
    """Schema for updating a pull request."""

    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    state: Optional[str] = None
    files_changed: Optional[int] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None


class PullRequestResponse(PullRequestBase):
    """Schema for pull request response."""

    id: Union[str, UUID]
    repository_id: Union[str, UUID]
    base_branch: Optional[str] = None
    head_branch: Optional[str] = None
    files_changed: Optional[int] = None
    additions: Optional[int] = None
    deletions: Optional[int] = None
    github_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id", "repository_id")
    def serialize_uuid(self, v: Union[str, UUID], _info) -> str:
        """Convert UUID to string."""
        return str(v)


class PullRequestList(BaseModel):
    """Schema for list of pull requests."""

    pull_requests: list[PullRequestResponse]
    total: int
