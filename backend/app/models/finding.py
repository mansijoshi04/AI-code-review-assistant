"""
Finding model for storing individual code review findings.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Finding(Base):
    """
    Finding model representing an individual code review issue.

    Relationships:
        - review: Many-to-one with Review
    """

    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(
        String(50), nullable=True
    )  # security, quality, performance, style, ai_suggestion
    severity = Column(String(20), nullable=True, index=True)  # critical, warning, info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=True)
    line_number = Column(Integer, nullable=True)
    code_snippet = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    tool_source = Column(
        String(100), nullable=True
    )  # bandit, pylint, radon, claude, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    review = relationship("Review", back_populates="findings")

    def __repr__(self):
        return f"<Finding(id={self.id}, severity='{self.severity}', category='{self.category}', title='{self.title[:30]}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "review_id": str(self.review_id),
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
            "tool_source": self.tool_source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
