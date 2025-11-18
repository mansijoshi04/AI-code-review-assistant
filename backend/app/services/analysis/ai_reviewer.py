"""
AI-powered code reviewer using Claude API.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from app.services.analysis.base import BaseAnalyzer, AnalyzerResult
from app.services.claude_service import claude_service


class AIReviewer(BaseAnalyzer):
    """AI-powered code reviewer using Claude API."""

    def __init__(self):
        """Initialize AI reviewer."""
        self.name = "AI Reviewer"

    async def analyze(
        self, files: Dict[str, str], workspace: Path, pr_context: Dict[str, Any] = None
    ) -> AnalyzerResult:
        """
        Analyze code using Claude API for intelligent review.

        Args:
            files: Dictionary of filename -> file content
            workspace: Path to workspace directory (not used for AI review)
            pr_context: Optional PR context (title, description, etc.)

        Returns:
            AnalyzerResult with AI-generated findings
        """
        findings = []
        success = True
        error_message = None

        # Check if Claude API is available
        if not claude_service.is_available():
            return AnalyzerResult(
                tool="ai-claude",
                findings=[],
                success=False,
                error="Claude API key not configured. Set ANTHROPIC_API_KEY environment variable.",
            )

        # Limit total code size to avoid token limits
        # Claude 3.5 Sonnet has 200k context window, but we'll be conservative
        max_chars = 50000  # ~12.5k tokens approximately
        truncated_files = self._truncate_files(files, max_chars)

        if len(truncated_files) == 0:
            return AnalyzerResult(
                tool="ai-claude",
                findings=[],
                success=True,
                error=None,
            )

        try:
            # Call Claude API for code review
            response = await claude_service.review_code(
                files=truncated_files,
                pr_context=pr_context,
            )

            # Parse JSON response
            findings = self._parse_ai_response(response)

        except Exception as e:
            success = False
            error_message = f"AI review failed: {str(e)}"
            print(f"AI Reviewer error: {error_message}")

        return AnalyzerResult(
            tool="ai-claude",
            findings=findings,
            success=success,
            error=error_message,
        )

    def _truncate_files(
        self, files: Dict[str, str], max_chars: int
    ) -> Dict[str, str]:
        """
        Truncate files to fit within character limit.

        Prioritizes smaller files and includes as many as possible.

        Args:
            files: Dictionary of filename -> file content
            max_chars: Maximum total characters

        Returns:
            Truncated dictionary of files
        """
        # Sort files by size (smallest first)
        sorted_files = sorted(files.items(), key=lambda x: len(x[1]))

        truncated = {}
        total_chars = 0

        for filename, content in sorted_files:
            file_size = len(content)
            if total_chars + file_size <= max_chars:
                truncated[filename] = content
                total_chars += file_size
            else:
                # Check if we can include a truncated version
                remaining = max_chars - total_chars
                if remaining > 1000:  # Only include if we can get at least 1000 chars
                    truncated[filename] = content[:remaining] + "\n\n... (truncated)"
                break

        return truncated

    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse Claude's JSON response into findings.

        Args:
            response: Raw response from Claude

        Returns:
            List of finding dictionaries
        """
        findings = []

        try:
            # Extract JSON from response (may be wrapped in markdown code blocks)
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r"\{.*\}", response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    print(f"No JSON found in AI response: {response[:500]}")
                    # Create a generic finding from the text response
                    return [{
                        "category": "ai-review",
                        "severity": "info",
                        "title": "AI Code Review",
                        "description": response[:1000] if response else "No feedback provided",
                        "file_path": None,
                        "line_number": None,
                        "code_snippet": None,
                        "suggestion": "Review the AI-generated feedback above",
                        "tool_source": "ai-claude",
                    }]

            # Parse JSON
            data = json.loads(json_str)

            # Extract findings
            ai_findings = data.get("findings", [])

            for finding in ai_findings:
                # Map AI categories to our standard categories
                category = self._map_category(finding.get("category", "best-practices"))
                severity = finding.get("severity", "info").lower()

                # Validate severity
                if severity not in ["critical", "warning", "info"]:
                    severity = "info"

                finding_dict = {
                    "category": category,
                    "severity": severity,
                    "title": finding.get("title", "AI Review Finding"),
                    "description": finding.get("description", ""),
                    "file_path": finding.get("file_path"),
                    "line_number": finding.get("line_number"),
                    "code_snippet": finding.get("code_snippet"),
                    "suggestion": finding.get("suggestion"),
                    "tool_source": "ai-claude",
                }

                findings.append(finding_dict)

        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"Response: {response[:500]}")
            # Create a generic finding from the text response
            findings.append({
                "category": "ai-review",
                "severity": "info",
                "title": "AI Code Review",
                "description": response[:1000],  # Truncate to 1000 chars
                "file_path": None,
                "line_number": None,
                "code_snippet": None,
                "suggestion": "Review the AI-generated feedback above",
                "tool_source": "ai-claude",
            })
        except Exception as e:
            print(f"Error parsing AI response: {e}")

        return findings

    def _map_category(self, ai_category: str) -> str:
        """
        Map AI category names to standard categories.

        Args:
            ai_category: Category from Claude

        Returns:
            Standardized category name
        """
        category_map = {
            "best-practices": "best-practices",
            "design": "design",
            "error-handling": "error-handling",
            "performance": "performance",
            "maintainability": "maintainability",
            "testing": "testing",
            "architecture": "architecture",
            "security": "security",  # Claude might identify security issues too
            "quality": "quality",
        }

        return category_map.get(ai_category.lower(), "ai-review")


# Global AI reviewer instance
ai_reviewer = AIReviewer()
