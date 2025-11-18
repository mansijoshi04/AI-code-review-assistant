"""
Pydantic schemas for Repository model.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class RepositoryBase(BaseModel):
    """Base Repository schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255)
    full_name: str = Field(..., min_length=1, max_length=255)
    owner: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class RepositoryCreate(RepositoryBase):
    """Schema for creating a new repository."""

    github_id: int = Field(..., gt=0)
    webhook_id: Optional[int] = None


class RepositoryUpdate(BaseModel):
    """Schema for updating a repository."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    owner: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    webhook_id: Optional[int] = None


class RepositoryResponse(RepositoryBase):
    """Schema for repository response."""

    id: Union[str, UUID]
    user_id: Union[str, UUID]
    github_id: int
    webhook_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('id', 'user_id')
    def serialize_uuid(self, v: Union[str, UUID], _info) -> str:
        """Convert UUID to string."""
        return str(v)


class RepositoryList(BaseModel):
    """Schema for list of repositories."""

    repositories: list[RepositoryResponse]
    total: int
