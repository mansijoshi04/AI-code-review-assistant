"""
GitHub webhook API endpoints.
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import json
from app.database import get_db
from app.services.github_service import github_service
from app.schemas.webhook import (
    PullRequestWebhookPayload,
    PullRequestReviewWebhookPayload,
    PullRequestReviewCommentWebhookPayload,
)

router = APIRouter()


@router.post("/github")
async def github_webhook_handler(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """
    Handle incoming GitHub webhook events.

    GitHub sends webhook events for various repository activities.
    This endpoint receives them, verifies the signature, and processes
    pull request events.

    Headers:
        X-GitHub-Event: Type of event (pull_request, pull_request_review, etc.)
        X-Hub-Signature-256: HMAC signature for verification

    Args:
        request: FastAPI request object
        x_github_event: Event type from header
        x_hub_signature_256: Signature from header
        db: Database session

    Returns:
        Dict with status message

    Raises:
        HTTPException: If signature verification fails or processing fails
    """
    # Read raw body for signature verification
    body = await request.body()

    # Verify webhook signature
    if not github_service.verify_webhook_signature(body, x_hub_signature_256 or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    # Parse JSON payload
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    # Route to appropriate handler based on event type
    if x_github_event == "pull_request":
        return await handle_pull_request_event(payload, db)
    elif x_github_event == "pull_request_review":
        return await handle_pull_request_review_event(payload, db)
    elif x_github_event == "pull_request_review_comment":
        return await handle_pull_request_review_comment_event(payload, db)
    elif x_github_event == "ping":
        # GitHub sends ping event when webhook is first created
        return {"status": "success", "message": "Pong! Webhook is configured correctly."}
    else:
        # Ignore other event types
        return {
            "status": "ignored",
            "message": f"Event type '{x_github_event}' not handled",
        }


async def handle_pull_request_event(payload: dict, db: Session) -> dict:
    """
    Handle pull_request webhook events.

    Triggered when: PR is opened, closed, reopened, edited, synchronized, etc.

    Args:
        payload: Webhook payload
        db: Database session

    Returns:
        Dict with status message
    """
    try:
        # Validate payload
        webhook_data = PullRequestWebhookPayload(**payload)

        # Import here to avoid circular dependency
        from app.services.pull_request_service import pull_request_service

        # Process based on action
        if webhook_data.action == "opened":
            await pull_request_service.process_pr_opened(webhook_data, db)
            return {
                "status": "success",
                "message": f"Processing new PR #{webhook_data.number}",
            }

        elif webhook_data.action == "synchronize":
            # PR was updated with new commits
            await pull_request_service.process_pr_updated(webhook_data, db)
            return {
                "status": "success",
                "message": f"Processing updated PR #{webhook_data.number}",
            }

        elif webhook_data.action == "closed":
            await pull_request_service.process_pr_closed(webhook_data, db)
            return {
                "status": "success",
                "message": f"Processed closed PR #{webhook_data.number}",
            }

        else:
            # Other actions (edited, labeled, etc.) - acknowledge but don't process
            return {
                "status": "acknowledged",
                "message": f"PR #{webhook_data.number} action '{webhook_data.action}' acknowledged",
            }

    except Exception as e:
        # Log error but return success to GitHub (avoid retries for application errors)
        print(f"Error processing pull request webhook: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to process webhook: {str(e)}",
        }


async def handle_pull_request_review_event(payload: dict, db: Session) -> dict:
    """
    Handle pull_request_review webhook events.

    Triggered when: A review is submitted, edited, or dismissed

    Args:
        payload: Webhook payload
        db: Database session

    Returns:
        Dict with status message
    """
    try:
        # Validate payload
        webhook_data = PullRequestReviewWebhookPayload(**payload)

        # For now, just acknowledge the event
        # In future sprints, we might want to re-run analysis when reviews are submitted
        return {
            "status": "acknowledged",
            "message": f"Review {webhook_data.action} for PR #{webhook_data.pull_request.number}",
        }

    except Exception as e:
        print(f"Error processing pull request review webhook: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to process webhook: {str(e)}",
        }


async def handle_pull_request_review_comment_event(payload: dict, db: Session) -> dict:
    """
    Handle pull_request_review_comment webhook events.

    Triggered when: A comment is created, edited, or deleted on a PR review

    Args:
        payload: Webhook payload
        db: Database session

    Returns:
        Dict with status message
    """
    try:
        # Validate payload
        webhook_data = PullRequestReviewCommentWebhookPayload(**payload)

        # For now, just acknowledge the event
        return {
            "status": "acknowledged",
            "message": f"Review comment {webhook_data.action} for PR #{webhook_data.pull_request.number}",
        }

    except Exception as e:
        print(f"Error processing pull request review comment webhook: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to process webhook: {str(e)}",
        }
