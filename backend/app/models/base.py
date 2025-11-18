"""
Base model with common fields for all database models.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """
    Mixin that adds timestamp fields to models.
    """

    @declared_attr
    def created_at(cls):
        """Timestamp when the record was created."""
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        """Timestamp when the record was last updated."""
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )
