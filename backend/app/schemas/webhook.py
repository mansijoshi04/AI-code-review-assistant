"""
Pydantic schemas for GitHub webhook payloads.
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class WebhookRepository(BaseModel):
    """GitHub repository in webhook payload."""

    id: int
    name: str
    full_name: str
    private: bool
    owner: Dict[str, Any]
    html_url: str
    description: Optional[str] = None


class WebhookPullRequest(BaseModel):
    """GitHub pull request in webhook payload."""

    id: int
    number: int
    state: str
    title: str
    body: Optional[str] = None
    user: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    head: Dict[str, Any]
    base: Dict[str, Any]
    html_url: str
    diff_url: str
    patch_url: str
    additions: Optional[int] = None
    deletions: Optional[int] = None
    changed_files: Optional[int] = None


class PullRequestWebhookPayload(BaseModel):
    """GitHub pull request webhook payload."""

    action: Literal[
        "opened",
        "edited",
        "closed",
        "reopened",
        "synchronize",
        "assigned",
        "unassigned",
        "review_requested",
        "review_request_removed",
        "labeled",
        "unlabeled",
        "locked",
        "unlocked",
    ]
    number: int
    pull_request: WebhookPullRequest
    repository: WebhookRepository
    sender: Dict[str, Any]
    installation: Optional[Dict[str, Any]] = None


class PullRequestReviewWebhookPayload(BaseModel):
    """GitHub pull request review webhook payload."""

    action: Literal["submitted", "edited", "dismissed"]
    review: Dict[str, Any]
    pull_request: WebhookPullRequest
    repository: WebhookRepository
    sender: Dict[str, Any]


class PullRequestReviewCommentWebhookPayload(BaseModel):
    """GitHub pull request review comment webhook payload."""

    action: Literal["created", "edited", "deleted"]
    comment: Dict[str, Any]
    pull_request: WebhookPullRequest
    repository: WebhookRepository
    sender: Dict[str, Any]
