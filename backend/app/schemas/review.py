"""
Pydantic schemas for Review model.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class ReviewBase(BaseModel):
    """Base Review schema with common fields."""

    status: Optional[str] = Field(
        None, description="Review status (pending, in_progress, completed, failed)"
    )
    overall_score: Optional[int] = Field(
        None, ge=0, le=100, description="Overall score (0-100)"
    )
    summary: Optional[str] = None


class ReviewCreate(BaseModel):
    """Schema for creating a new review."""

    pull_request_id: str


class ReviewUpdate(BaseModel):
    """Schema for updating a review."""

    status: Optional[str] = None
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    summary: Optional[str] = None
    critical_count: Optional[int] = None
    warning_count: Optional[int] = None
    info_count: Optional[int] = None


class ReviewResponse(ReviewBase):
    """Schema for review response."""

    id: Union[str, UUID]
    pull_request_id: Union[str, UUID]
    critical_count: int
    warning_count: int
    info_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id", "pull_request_id")
    def serialize_uuid(self, v: Union[str, UUID], _info) -> str:
        """Convert UUID to string."""
        return str(v)


class ReviewList(BaseModel):
    """Schema for list of reviews."""

    reviews: list[ReviewResponse]
    total: int


class ReviewStats(BaseModel):
    """Schema for review statistics."""

    total_reviews: int
    pending_reviews: int
    completed_reviews: int
    failed_reviews: int
    avg_score: Optional[float] = None
    total_critical_findings: int
    total_warning_findings: int
    total_info_findings: int
