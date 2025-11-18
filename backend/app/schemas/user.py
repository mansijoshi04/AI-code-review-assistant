"""
Pydantic schemas for User model.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class UserBase(BaseModel):
    """Base User schema with common fields."""

    username: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    github_id: int = Field(..., gt=0)
    access_token: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    username: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    access_token: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response (excludes sensitive data)."""

    id: Union[str, UUID]
    github_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('id')
    def serialize_id(self, v: Union[str, UUID], _info) -> str:
        """Convert UUID to string."""
        return str(v)


class UserWithToken(UserResponse):
    """Schema for user response with access token."""

    access_token: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for data stored in JWT token."""

    sub: str  # User ID
    github_id: int
    username: str
