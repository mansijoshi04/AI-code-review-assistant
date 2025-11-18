"""
User model for storing GitHub user information.
"""

import uuid
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """
    User model representing a GitHub user.

    Relationships:
        - repositories: One-to-many with Repository
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)  # TODO: Encrypt this in production

    # Relationships
    repositories = relationship(
        "Repository",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', github_id={self.github_id})>"

    def to_dict(self):
        """Convert model to dictionary (excluding sensitive data)."""
        return {
            "id": str(self.id),
            "github_id": self.github_id,
            "username": self.username,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
