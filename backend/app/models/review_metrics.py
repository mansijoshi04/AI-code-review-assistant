"""
ReviewMetrics model for storing aggregated analytics data.
"""

import uuid
from datetime import datetime, date as date_type
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Date,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import GUID


class ReviewMetrics(Base):
    """
    ReviewMetrics model for storing daily aggregated review statistics.

    Relationships:
        - repository: Many-to-one with Repository
    """

    __tablename__ = "review_metrics"
    __table_args__ = (
        UniqueConstraint("repository_id", "date", name="uq_repo_metrics_date"),
    )

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    repository_id = Column(
        GUID,
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(Date, nullable=False, index=True)
    total_reviews = Column(Integer, default=0, nullable=False)
    avg_score = Column(Numeric(5, 2), nullable=True)  # Average score (0-100)
    total_findings = Column(Integer, default=0, nullable=False)
    critical_findings = Column(Integer, default=0, nullable=False)
    avg_review_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    repository = relationship("Repository", back_populates="review_metrics")

    def __repr__(self):
        return f"<ReviewMetrics(id={self.id}, repository_id={self.repository_id}, date={self.date}, total_reviews={self.total_reviews})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "repository_id": str(self.repository_id),
            "date": self.date.isoformat() if self.date else None,
            "total_reviews": self.total_reviews,
            "avg_score": float(self.avg_score) if self.avg_score else None,
            "total_findings": self.total_findings,
            "critical_findings": self.critical_findings,
            "avg_review_time_seconds": self.avg_review_time_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
