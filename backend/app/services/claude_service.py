"""
Claude API service for AI-powered code review.
"""

import anthropic
from typing import List, Dict, Any, Optional
from app.config import settings


class ClaudeService:
    """Service for interacting with Anthropic Claude API."""

    def __init__(self):
        """Initialize Claude API client."""
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.temperature = settings.ANTHROPIC_TEMPERATURE

    def is_available(self) -> bool:
        """Check if Claude API is available (API key configured)."""
        return self.client is not None

    async def review_code(
        self,
        files: Dict[str, str],
        pr_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Review code using Claude API.

        Args:
            files: Dictionary of filename -> file content
            pr_context: Optional PR context (title, description, etc.)

        Returns:
            str: AI-generated review response

        Raises:
            Exception: If API call fails
        """
        if not self.is_available():
            raise Exception("Claude API key not configured")

        # Build the review prompt
        prompt = self._build_review_prompt(files, pr_context)

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract response text
            response_text = ""
            for block in message.content:
                if block.type == "text":
                    response_text += block.text

            return response_text

        except Exception as e:
            raise Exception(f"Claude API call failed: {str(e)}")

    def _build_review_prompt(
        self,
        files: Dict[str, str],
        pr_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a comprehensive review prompt for Claude.

        Args:
            files: Dictionary of filename -> file content
            pr_context: Optional PR context

        Returns:
            str: Formatted prompt
        """
        prompt_parts = [
            "You are an expert code reviewer. Please review the following Python code changes.",
            "",
            "Focus on:",
            "1. **Best Practices**: Adherence to Python best practices and idioms",
            "2. **Design Patterns**: Appropriate use of design patterns",
            "3. **Error Handling**: Proper exception handling and edge cases",
            "4. **Performance**: Potential performance issues or optimizations",
            "5. **Maintainability**: Code clarity, documentation, and long-term maintainability",
            "6. **Testing**: Testability and test coverage considerations",
            "7. **Architecture**: Overall design and architectural concerns",
            "",
        ]

        # Add PR context if available
        if pr_context:
            prompt_parts.extend([
                "## Pull Request Context",
                f"**Title**: {pr_context.get('title', 'N/A')}",
                f"**Description**: {pr_context.get('description', 'N/A')}",
                "",
            ])

        # Add files to review
        prompt_parts.append("## Code Changes")
        prompt_parts.append("")

        for filename, content in files.items():
            prompt_parts.extend([
                f"### File: `{filename}`",
                "```python",
                content,
                "```",
                "",
            ])

        # Add review instructions
        prompt_parts.extend([
            "## Review Instructions",
            "",
            "Provide your review in the following JSON format:",
            "```json",
            "{",
            '  "findings": [',
            "    {",
            '      "category": "best-practices|design|error-handling|performance|maintainability|testing|architecture",',
            '      "severity": "critical|warning|info",',
            '      "title": "Brief title of the issue",',
            '      "description": "Detailed explanation of the issue",',
            '      "file_path": "path/to/file.py",',
            '      "line_number": 42,',
            '      "code_snippet": "problematic code snippet",',
            '      "suggestion": "How to fix or improve this"',
            "    }",
            "  ],",
            '  "summary": "Overall assessment of the code quality and key recommendations"',
            "}",
            "```",
            "",
            "Guidelines:",
            "- Only report genuine issues, not nitpicks",
            "- Prioritize critical issues (security, bugs, major design flaws)",
            "- Be constructive and specific in your suggestions",
            "- Include line numbers when referencing specific code",
            "- If the code is excellent, say so with minimal or no findings",
        ])

        return "\n".join(prompt_parts)

    async def analyze_findings(
        self, findings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze findings from other tools and provide additional context.

        Args:
            findings: List of findings from static analysis tools

        Returns:
            Dict with additional insights

        Raises:
            Exception: If API call fails
        """
        if not self.is_available():
            raise Exception("Claude API key not configured")

        # Build prompt for finding analysis
        prompt_parts = [
            "You are an expert code reviewer. The following issues were detected by automated tools.",
            "Please provide additional context, prioritization, and recommendations.",
            "",
            "## Detected Issues",
            "",
        ]

        for i, finding in enumerate(findings, 1):
            prompt_parts.extend([
                f"### Issue {i}",
                f"**Category**: {finding.get('category', 'unknown')}",
                f"**Severity**: {finding.get('severity', 'info')}",
                f"**Title**: {finding.get('title', 'N/A')}",
                f"**Description**: {finding.get('description', 'N/A')}",
                f"**File**: {finding.get('file_path', 'N/A')}:{finding.get('line_number', 'N/A')}",
                "",
            ])

        prompt_parts.extend([
            "## Analysis Request",
            "",
            "Please provide:",
            "1. Overall risk assessment (low/medium/high)",
            "2. Top 3 most critical issues that should be addressed immediately",
            "3. Recommended action plan",
            "",
            "Respond in JSON format:",
            "```json",
            "{",
            '  "risk_level": "low|medium|high",',
            '  "critical_issues": ["issue 1", "issue 2", "issue 3"],',
            '  "action_plan": "Recommended steps to address the issues"',
            "}",
            "```",
        ])

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": "\n".join(prompt_parts)}],
            )

            response_text = ""
            for block in message.content:
                if block.type == "text":
                    response_text += block.text

            return {"analysis": response_text}

        except Exception as e:
            raise Exception(f"Claude API call failed: {str(e)}")


# Global Claude service instance
claude_service = ClaudeService()
