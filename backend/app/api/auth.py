"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_user_token
from app.models.user import User
from app.schemas.user import UserResponse, Token
from app.services.github_service import github_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user information.

    Returns:
        UserResponse: Current user data
    """
    return UserResponse.model_validate(current_user)


@router.post("/token", response_model=Token)
async def create_token(
    github_id: int,
    username: str,
    email: str = None,
    avatar_url: str = None,
    access_token: str = None,
    db: Session = Depends(get_db),
) -> Token:
    """
    Create a JWT token for a user (or create user if doesn't exist).
    This endpoint is typically called after GitHub OAuth flow.

    Args:
        github_id: GitHub user ID
        username: GitHub username
        email: User email
        avatar_url: User avatar URL
        access_token: GitHub access token
        db: Database session

    Returns:
        Token: JWT token response
    """
    # Check if user exists
    user = db.query(User).filter(User.github_id == github_id).first()

    if user is None:
        # Create new user
        user = User(
            github_id=github_id,
            username=username,
            email=email,
            avatar_url=avatar_url,
            access_token=access_token,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user
        user.username = username
        user.email = email
        user.avatar_url = avatar_url
        if access_token:
            user.access_token = access_token
        db.commit()
        db.refresh(user)

    # Create JWT token
    token = create_user_token(
        user_id=str(user.id), github_id=user.github_id, username=user.username
    )

    return Token(access_token=token, token_type="bearer")


@router.post("/github", response_model=Token)
async def github_oauth_callback(
    code: str,
    db: Session = Depends(get_db),
) -> Token:
    """
    Handle GitHub OAuth callback.

    This endpoint receives the authorization code from GitHub's OAuth flow,
    exchanges it for an access token, fetches user info, and creates/updates
    the user in our database.

    Args:
        code: OAuth authorization code from GitHub
        db: Database session

    Returns:
        Token: JWT token for our application

    Raises:
        HTTPException: If OAuth flow fails
    """
    try:
        # Step 1: Exchange code for access token
        access_token = await github_service.exchange_code_for_token(code)

        # Step 2: Fetch user info from GitHub
        github_user = await github_service.get_user_info(access_token)

        # Step 3: Create or update user in database
        user = db.query(User).filter(User.github_id == github_user["id"]).first()

        if user is None:
            # Create new user
            user = User(
                github_id=github_user["id"],
                username=github_user["login"],
                email=github_user.get("email"),
                avatar_url=github_user.get("avatar_url"),
                access_token=access_token,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user
            user.username = github_user["login"]
            user.email = github_user.get("email")
            user.avatar_url = github_user.get("avatar_url")
            user.access_token = access_token
            db.commit()
            db.refresh(user)

        # Step 4: Create JWT token for our application
        token = create_user_token(
            user_id=str(user.id),
            github_id=user.github_id,
            username=user.username,
        )

        return Token(access_token=token, token_type="bearer")

    except HTTPException:
        # Re-raise HTTP exceptions from GitHub service
        raise
    except Exception as e:
        # Log the error and return generic message
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub OAuth failed: {str(e)}",
        )
