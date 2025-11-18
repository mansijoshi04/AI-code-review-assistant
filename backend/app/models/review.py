"""
Review model for storing code review results.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Review(Base):
    """
    Review model representing a code review execution.

    Relationships:
        - pull_request: Many-to-one with PullRequest
        - findings: One-to-many with Finding
    """

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pull_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(
        String(50), nullable=True
    )  # pending, in_progress, completed, failed
    overall_score = Column(Integer, nullable=True)  # 0-100
    summary = Column(Text, nullable=True)
    critical_count = Column(Integer, default=0, nullable=False)
    warning_count = Column(Integer, default=0, nullable=False)
    info_count = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    pull_request = relationship("PullRequest", back_populates="reviews")
    findings = relationship(
        "Finding",
        back_populates="review",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<Review(id={self.id}, status='{self.status}', score={self.overall_score}, findings={self.critical_count}/{self.warning_count}/{self.info_count})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "pull_request_id": str(self.pull_request_id),
            "status": self.status,
            "overall_score": self.overall_score,
            "summary": self.summary,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
