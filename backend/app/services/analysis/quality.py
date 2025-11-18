"""
Code quality analyzer using Pylint and Radon.
"""

import json
import subprocess
from typing import Dict, List, Any
from pathlib import Path
from app.services.analysis.base import BaseAnalyzer, AnalyzerResult


class QualityAnalyzer(BaseAnalyzer):
    """Code quality analyzer using Pylint and Radon."""

    def __init__(self):
        """Initialize quality analyzer."""
        super().__init__("quality")
        self.pylint_severity_map = {
            "error": "critical",
            "warning": "warning",
            "refactor": "info",
            "convention": "info",
        }

    async def analyze(self, files: Dict[str, str], workspace: Path) -> AnalyzerResult:
        """
        Run Pylint quality analysis on Python files.

        Args:
            files: Dictionary of filename -> content
            workspace: Path to workspace directory

        Returns:
            AnalyzerResult: Quality analysis results
        """
        try:
            # Run Pylint on workspace
            result = subprocess.run(
                [
                    "pylint",
                    str(workspace),
                    "--output-format=json",
                    "--disable=all",  # Disable all then enable specific
                    "--enable=E,W,R",  # Enable errors, warnings, refactors
                    "--max-line-length=120",
                    "--good-names=i,j,k,v,f,fp,db",
                ],
                capture_output=True,
                text=True,
                timeout=90,  # 90 second timeout
            )

            # Parse JSON output
            if result.stdout:
                pylint_data = json.loads(result.stdout)
                findings = self._parse_pylint_output(pylint_data, workspace)
                return AnalyzerResult(
                    tool="pylint", findings=findings, success=True
                )
            else:
                # No issues found
                return AnalyzerResult(tool="pylint", findings=[], success=True)

        except subprocess.TimeoutExpired:
            return AnalyzerResult(
                tool="pylint",
                findings=[],
                success=False,
                error="Pylint analysis timed out",
            )
        except json.JSONDecodeError:
            # Pylint might output non-JSON when no issues found
            return AnalyzerResult(tool="pylint", findings=[], success=True)
        except Exception as e:
            return AnalyzerResult(
                tool="pylint", findings=[], success=False, error=str(e)
            )

    def _parse_pylint_output(
        self, pylint_data: List[Dict[str, Any]], workspace: Path
    ) -> List[Dict[str, Any]]:
        """
        Parse Pylint JSON output into findings.

        Args:
            pylint_data: Parsed JSON from Pylint (list of messages)
            workspace: Workspace path for relative path calculation

        Returns:
            List[Dict[str, Any]]: List of finding dictionaries
        """
        findings = []

        for message in pylint_data:
            # Get relative path from workspace
            file_path = Path(message["path"]).relative_to(workspace)

            # Generate suggestion based on message
            suggestion = self._generate_suggestion(
                message.get("symbol", ""), message.get("message", "")
            )

            finding = {
                "category": "quality",
                "severity": self._map_pylint_severity(message.get("type", "info")),
                "title": message.get("message", "Code quality issue"),
                "description": f"{message.get('message', '')} ({message.get('symbol', '')})",
                "file_path": str(file_path),
                "line_number": message.get("line", 0),
                "code_snippet": "",  # Pylint doesn't provide this
                "suggestion": suggestion,
                "tool_source": "pylint",
                "message_id": message.get("message-id", ""),
            }

            findings.append(finding)

        return findings

    def _map_pylint_severity(self, pylint_type: str) -> str:
        """
        Map Pylint message type to our standard levels.

        Args:
            pylint_type: Pylint type (error, warning, refactor, convention)

        Returns:
            str: Normalized severity (critical, warning, info)
        """
        return self.pylint_severity_map.get(pylint_type.lower(), "info")

    def _generate_suggestion(self, symbol: str, message: str) -> str:
        """
        Generate suggestion based on Pylint symbol.

        Args:
            symbol: Pylint message symbol
            message: Pylint message text

        Returns:
            str: Suggestion for fixing the issue
        """
        suggestions = {
            "unused-import": "Remove unused imports to keep code clean",
            "unused-variable": "Remove unused variables or use them in your code",
            "undefined-variable": "Define the variable before using it",
            "import-error": "Ensure the module is installed and importable",
            "no-member": "Check if the attribute/method exists on this object",
            "too-many-arguments": "Refactor to use fewer arguments or a configuration object",
            "too-many-locals": "Refactor into smaller functions",
            "too-many-branches": "Refactor to reduce conditional complexity",
            "too-many-statements": "Break down into smaller, focused functions",
            "line-too-long": "Break long lines into multiple lines (max 120 chars)",
            "missing-docstring": "Add docstring to explain function/class purpose",
            "invalid-name": "Use descriptive, PEP 8 compliant names",
            "redefined-outer-name": "Use different variable name to avoid shadowing",
            "broad-except": "Catch specific exceptions instead of bare except",
            "bare-except": "Never use bare except, catch specific exceptions",
            "consider-using-enumerate": "Use enumerate() for cleaner iteration",
            "consider-using-dict-items": "Use .items() instead of .keys()",
            "simplifiable-if-expression": "Simplify the conditional expression",
        }

        return suggestions.get(symbol, f"Review and fix: {message}")


# Global quality analyzer instance
quality_analyzer = QualityAnalyzer()
