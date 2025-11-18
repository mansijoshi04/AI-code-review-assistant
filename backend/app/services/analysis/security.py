"""
Security analyzer using Bandit.
"""

import json
import subprocess
from typing import Dict, List, Any
from pathlib import Path
from app.services.analysis.base import BaseAnalyzer, AnalyzerResult


class SecurityAnalyzer(BaseAnalyzer):
    """Security vulnerability analyzer using Bandit."""

    def __init__(self):
        """Initialize security analyzer."""
        super().__init__("bandit")
        self.severity_map = {
            "HIGH": "critical",
            "MEDIUM": "warning",
            "LOW": "info",
        }
        self.suggestions = {
            "B105": "Use environment variables or secure configuration management instead of hardcoded passwords",
            "B106": "Use environment variables or secure configuration management instead of hardcoded passwords",
            "B107": "Use environment variables or secure configuration management instead of hardcoded passwords",
            "B201": "Avoid using wildcard imports, import only what you need",
            "B301": "Use pickle alternatives like json or safer serialization methods",
            "B302": "Use safe YAML loading methods like yaml.safe_load()",
            "B303": "Avoid using MD5 or SHA1 for security purposes, use SHA256 or better",
            "B304": "Avoid using insecure ciphers, use AES with secure key management",
            "B305": "Avoid using insecure ciphers, use AES with secure key management",
            "B306": "Use tempfile.mkstemp() or tempfile.TemporaryFile() for secure temporary files",
            "B307": "Use eval() alternatives like ast.literal_eval() for safer evaluation",
            "B308": "Validate and sanitize user input before using mark_safe()",
            "B309": "Use parameterized queries to prevent SQL injection",
            "B310": "Validate and sanitize URLs before using them",
            "B311": "Use secrets module instead of random for cryptographic purposes",
            "B312": "Use cryptographically secure random functions from secrets module",
            "B313": "Use cryptographically secure random functions from secrets module",
            "B314": "Validate and sanitize XML input to prevent XXE attacks",
            "B315": "Validate and sanitize XML input to prevent XXE attacks",
            "B316": "Validate and sanitize XML input to prevent XXE attacks",
            "B317": "Validate and sanitize XML input to prevent XXE attacks",
            "B318": "Validate and sanitize XML input to prevent XXE attacks",
            "B319": "Validate and sanitize XML input to prevent XXE attacks",
            "B320": "Validate and sanitize XML input to prevent XXE attacks",
            "B321": "Use httpx or requests with proper certificate validation",
            "B322": "Validate user input before using in format strings",
            "B323": "Avoid unverified HTTPS connections, enable certificate verification",
            "B324": "Use secure hash algorithms like SHA256 or SHA3",
            "B325": "Use tempfile module for secure temporary file handling",
            "B501": "Validate and sanitize user input, escape output properly",
            "B502": "Enable SSL/TLS certificate verification for secure connections",
            "B503": "Enable SSL/TLS certificate verification for secure connections",
            "B504": "Enable SSL/TLS certificate verification for secure connections",
            "B505": "Use cryptographically secure random functions",
            "B506": "Validate YAML input and use safe loading methods",
            "B507": "Avoid using SSH with password authentication, use key-based auth",
            "B601": "Avoid shell=True in subprocess, use list arguments instead",
            "B602": "Validate and sanitize all inputs to shell commands",
            "B603": "Avoid shell=True in subprocess, validate all inputs",
            "B604": "Validate and sanitize function arguments",
            "B605": "Validate and escape all command arguments",
            "B606": "Avoid shell=True in subprocess calls",
            "B607": "Avoid shell=True, use absolute paths for executables",
            "B608": "Use parameterized queries to prevent SQL injection",
            "B609": "Use parameterized queries to prevent SQL injection",
            "B610": "Use parameterized queries to prevent SQL injection",
            "B611": "Use parameterized queries to prevent SQL injection",
            "B701": "Use jinja2 with autoescape enabled",
            "B702": "Use Mako with default_filters enabled",
            "B703": "Validate and sanitize user input in Django applications",
        }

    async def analyze(self, files: Dict[str, str], workspace: Path) -> AnalyzerResult:
        """
        Run Bandit security analysis on Python files.

        Args:
            files: Dictionary of filename -> content
            workspace: Path to workspace directory

        Returns:
            AnalyzerResult: Security analysis results
        """
        try:
            # Run Bandit on workspace
            result = subprocess.run(
                [
                    "bandit",
                    "-r",  # Recursive
                    str(workspace),
                    "-f",
                    "json",  # JSON output
                    "-ll",  # Low level and above
                ],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
            )

            # Parse JSON output
            if result.stdout:
                bandit_data = json.loads(result.stdout)
                findings = self._parse_bandit_output(bandit_data, workspace)
                return AnalyzerResult(
                    tool="bandit", findings=findings, success=True
                )
            else:
                # No issues found or error
                return AnalyzerResult(tool="bandit", findings=[], success=True)

        except subprocess.TimeoutExpired:
            return AnalyzerResult(
                tool="bandit",
                findings=[],
                success=False,
                error="Bandit analysis timed out",
            )
        except json.JSONDecodeError:
            return AnalyzerResult(
                tool="bandit",
                findings=[],
                success=False,
                error="Failed to parse Bandit output",
            )
        except Exception as e:
            return AnalyzerResult(
                tool="bandit", findings=[], success=False, error=str(e)
            )

    def _parse_bandit_output(
        self, bandit_data: Dict[str, Any], workspace: Path
    ) -> List[Dict[str, Any]]:
        """
        Parse Bandit JSON output into findings.

        Args:
            bandit_data: Parsed JSON from Bandit
            workspace: Workspace path for relative path calculation

        Returns:
            List[Dict[str, Any]]: List of finding dictionaries
        """
        findings = []

        for result in bandit_data.get("results", []):
            # Get relative path from workspace
            file_path = Path(result["filename"]).relative_to(workspace)

            # Extract code snippet (get the line from code if available)
            code_snippet = result.get("code", "").strip()

            # Generate suggestion based on test_id
            test_id = result.get("test_id", "")
            suggestion = self.suggestions.get(
                test_id, "Review and fix this security issue"
            )

            finding = {
                "category": "security",
                "severity": self._map_severity(result["issue_severity"]),
                "title": result["issue_text"],
                "description": f"{result['issue_text']} ({test_id}: {result['test_name']})",
                "file_path": str(file_path),
                "line_number": result["line_number"],
                "code_snippet": code_snippet,
                "suggestion": suggestion,
                "tool_source": "bandit",
                "confidence": result.get("issue_confidence", "MEDIUM"),
            }

            findings.append(finding)

        return findings

    def _map_severity(self, bandit_severity: str) -> str:
        """
        Map Bandit severity to our standard levels.

        Args:
            bandit_severity: Bandit severity (HIGH, MEDIUM, LOW)

        Returns:
            str: Normalized severity (critical, warning, info)
        """
        return self.severity_map.get(bandit_severity.upper(), "info")


# Global security analyzer instance
security_analyzer = SecurityAnalyzer()
