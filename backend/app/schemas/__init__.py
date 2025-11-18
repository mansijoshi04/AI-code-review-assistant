"""
Pydantic schemas for API request/response validation.
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithToken,
    Token,
    TokenData,
)
from app.schemas.repository import (
    RepositoryBase,
    RepositoryCreate,
    RepositoryUpdate,
    RepositoryResponse,
    RepositoryList,
)
from app.schemas.pull_request import (
    PullRequestBase,
    PullRequestCreate,
    PullRequestUpdate,
    PullRequestResponse,
    PullRequestList,
)
from app.schemas.webhook import (
    PullRequestWebhookPayload,
    PullRequestReviewWebhookPayload,
    PullRequestReviewCommentWebhookPayload,
)
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewList,
    ReviewStats,
)
from app.schemas.finding import (
    FindingBase,
    FindingCreate,
    FindingUpdate,
    FindingResponse,
    FindingList,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithToken",
    "Token",
    "TokenData",
    # Repository schemas
    "RepositoryBase",
    "RepositoryCreate",
    "RepositoryUpdate",
    "RepositoryResponse",
    "RepositoryList",
    # Pull request schemas
    "PullRequestBase",
    "PullRequestCreate",
    "PullRequestUpdate",
    "PullRequestResponse",
    "PullRequestList",
    # Webhook schemas
    "PullRequestWebhookPayload",
    "PullRequestReviewWebhookPayload",
    "PullRequestReviewCommentWebhookPayload",
    # Review schemas
    "ReviewBase",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewList",
    "ReviewStats",
    # Finding schemas
    "FindingBase",
    "FindingCreate",
    "FindingUpdate",
    "FindingResponse",
    "FindingList",
]
