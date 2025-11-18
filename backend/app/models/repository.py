"""
Repository model for storing GitHub repository information.
"""

import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin


class Repository(Base, TimestampMixin):
    """
    Repository model representing a GitHub repository.

    Relationships:
        - user: Many-to-one with User
        - pull_requests: One-to-many with PullRequest
        - review_metrics: One-to-many with ReviewMetrics
    """

    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    webhook_id = Column(Integer, nullable=True)

    # Relationships
    user = relationship("User", back_populates="repositories")
    pull_requests = relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    review_metrics = relationship(
        "ReviewMetrics",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Repository(id={self.id}, full_name='{self.full_name}', is_active={self.is_active})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "github_id": self.github_id,
            "name": self.name,
            "full_name": self.full_name,
            "owner": self.owner,
            "is_active": self.is_active,
            "webhook_id": self.webhook_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
