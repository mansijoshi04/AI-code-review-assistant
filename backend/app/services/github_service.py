"""
GitHub API service for OAuth authentication and repository interactions.
"""

import httpx
import hmac
import hashlib
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from app.config import settings


class GitHubService:
    """Service for interacting with GitHub API."""

    def __init__(self):
        """Initialize GitHub service with configuration."""
        self.api_base_url = settings.GITHUB_API_BASE_URL
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.webhook_secret = settings.GITHUB_WEBHOOK_SECRET
        self.oauth_token_url = settings.GITHUB_OAUTH_TOKEN_URL

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange OAuth authorization code for access token.

        Args:
            code: OAuth authorization code from GitHub

        Returns:
            GitHub access token

        Raises:
            HTTPException: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.oauth_token_url,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": code,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token",
                )

            data = response.json()

            if "error" in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth error: {data.get('error_description', 'Unknown error')}",
                )

            return data["access_token"]

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get authenticated user information from GitHub.

        Args:
            access_token: GitHub access token

        Returns:
            User information dictionary

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch user info from GitHub",
                )

            return response.json()

    async def get_user_repositories(
        self, access_token: str, page: int = 1, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get list of repositories for authenticated user.

        Args:
            access_token: GitHub access token
            page: Page number (1-indexed)
            per_page: Results per page (max 100)

        Returns:
            List of repository dictionaries

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/user/repos",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={
                    "page": page,
                    "per_page": min(per_page, 100),
                    "sort": "updated",
                    "direction": "desc",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch repositories from GitHub",
                )

            return response.json()

    async def get_repository(
        self, access_token: str, owner: str, repo: str
    ) -> Dict[str, Any]:
        """
        Get details of a specific repository.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name

        Returns:
            Repository information dictionary

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/repos/{owner}/{repo}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Repository not found",
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch repository from GitHub",
                )

            return response.json()

    async def get_pull_requests(
        self,
        access_token: str,
        owner: str,
        repo: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Get list of pull requests for a repository.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            state: PR state (open, closed, all)
            page: Page number (1-indexed)
            per_page: Results per page (max 100)

        Returns:
            List of pull request dictionaries

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/repos/{owner}/{repo}/pulls",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                params={
                    "state": state,
                    "page": page,
                    "per_page": min(per_page, 100),
                    "sort": "updated",
                    "direction": "desc",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch pull requests from GitHub",
                )

            return response.json()

    async def get_pull_request(
        self, access_token: str, owner: str, repo: str, pull_number: int
    ) -> Dict[str, Any]:
        """
        Get details of a specific pull request.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            pull_number: Pull request number

        Returns:
            Pull request information dictionary

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/repos/{owner}/{repo}/pulls/{pull_number}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pull request not found",
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch pull request from GitHub",
                )

            return response.json()

    async def get_pull_request_diff(
        self, access_token: str, owner: str, repo: str, pull_number: int
    ) -> str:
        """
        Get diff content for a pull request.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            pull_number: Pull request number

        Returns:
            Diff content as string

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/repos/{owner}/{repo}/pulls/{pull_number}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3.diff",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch pull request diff from GitHub",
                )

            return response.text

    async def get_pull_request_files(
        self, access_token: str, owner: str, repo: str, pull_number: int
    ) -> List[Dict[str, Any]]:
        """
        Get list of files changed in a pull request.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            pull_number: Pull request number

        Returns:
            List of file change dictionaries

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/repos/{owner}/{repo}/pulls/{pull_number}/files",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch pull request files from GitHub",
                )

            return response.json()

    async def create_webhook(
        self, access_token: str, owner: str, repo: str, webhook_url: str
    ) -> Dict[str, Any]:
        """
        Create a webhook for a repository.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            webhook_url: URL to receive webhook events

        Returns:
            Webhook information dictionary

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/repos/{owner}/{repo}/hooks",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json={
                    "name": "web",
                    "active": True,
                    "events": [
                        "pull_request",
                        "pull_request_review",
                        "pull_request_review_comment",
                    ],
                    "config": {
                        "url": webhook_url,
                        "content_type": "json",
                        "secret": self.webhook_secret,
                        "insecure_ssl": "0",
                    },
                },
            )

            if response.status_code == 422:
                # Webhook might already exist
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Webhook already exists for this repository",
                )
            elif response.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create webhook",
                )

            return response.json()

    async def delete_webhook(
        self, access_token: str, owner: str, repo: str, webhook_id: int
    ) -> None:
        """
        Delete a webhook from a repository.

        Args:
            access_token: GitHub access token
            owner: Repository owner (username or org)
            repo: Repository name
            webhook_id: Webhook ID to delete

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_base_url}/repos/{owner}/{repo}/hooks/{webhook_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook not found",
                )
            elif response.status_code != 204:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to delete webhook",
                )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature.

        Args:
            payload: Raw request body bytes
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid, False otherwise
        """
        if not signature:
            return False

        # GitHub sends signature as "sha256=<hash>"
        if not signature.startswith("sha256="):
            return False

        expected_signature = signature[7:]  # Remove "sha256=" prefix

        # Calculate HMAC
        mac = hmac.new(
            self.webhook_secret.encode("utf-8"), msg=payload, digestmod=hashlib.sha256
        )
        computed_signature = mac.hexdigest()

        # Compare signatures securely
        return hmac.compare_digest(computed_signature, expected_signature)


# Global GitHub service instance
github_service = GitHubService()
