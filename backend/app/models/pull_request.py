"""
PullRequest model for storing GitHub pull request information.
"""

import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import TimestampMixin, GUID


class PullRequest(Base, TimestampMixin):
    """
    PullRequest model representing a GitHub pull request.

    Relationships:
        - repository: Many-to-one with Repository
        - reviews: One-to-many with Review
    """

    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repository_id", "pr_number", name="uq_repo_pr_number"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    repository_id = Column(
        GUID,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pr_number = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    author = Column(String(255), nullable=True)
    state = Column(String(50), nullable=True)  # open, closed, merged
    base_branch = Column(String(255), nullable=True)
    head_branch = Column(String(255), nullable=True)
    files_changed = Column(Integer, nullable=True)
    additions = Column(Integer, nullable=True)
    deletions = Column(Integer, nullable=True)
    github_url = Column(Text, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    reviews = relationship(
        "Review",
        back_populates="pull_request",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<PullRequest(id={self.id}, pr_number={self.pr_number}, title='{self.title[:50]}', state='{self.state}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "repository_id": str(self.repository_id),
            "pr_number": self.pr_number,
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "state": self.state,
            "base_branch": self.base_branch,
            "head_branch": self.head_branch,
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
            "github_url": self.github_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
