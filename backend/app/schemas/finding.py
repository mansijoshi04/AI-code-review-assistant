"""
Pydantic schemas for Finding model.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class FindingBase(BaseModel):
    """Base Finding schema with common fields."""

    category: str = Field(..., description="Finding category (security, quality, complexity, etc.)")
    severity: str = Field(..., description="Severity level (critical, warning, info)")
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    tool_source: Optional[str] = None


class FindingCreate(FindingBase):
    """Schema for creating a new finding."""

    review_id: str


class FindingUpdate(BaseModel):
    """Schema for updating a finding."""

    category: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    suggestion: Optional[str] = None


class FindingResponse(FindingBase):
    """Schema for finding response."""

    id: Union[str, UUID]
    review_id: Union[str, UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id", "review_id")
    def serialize_uuid(self, v: Union[str, UUID], _info) -> str:
        """Convert UUID to string."""
        return str(v)


class FindingList(BaseModel):
    """Schema for list of findings."""

    findings: list[FindingResponse]
    total: int
    critical_count: int
    warning_count: int
    info_count: int
