"""
Base analyzer interface and utilities.
"""

import os
import tempfile
import shutil
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path


class AnalyzerResult:
    """Result from an analyzer."""

    def __init__(
        self,
        tool: str,
        findings: List[Dict[str, Any]],
        success: bool = True,
        error: str = None,
    ):
        """
        Initialize analyzer result.

        Args:
            tool: Name of the analysis tool
            findings: List of finding dictionaries
            success: Whether analysis completed successfully
            error: Error message if analysis failed
        """
        self.tool = tool
        self.findings = findings
        self.success = success
        self.error = error


class BaseAnalyzer(ABC):
    """Base class for code analyzers."""

    def __init__(self, name: str):
        """
        Initialize base analyzer.

        Args:
            name: Analyzer name
        """
        self.name = name

    @abstractmethod
    async def analyze(self, files: Dict[str, str], workspace: Path) -> AnalyzerResult:
        """
        Analyze code files.

        Args:
            files: Dictionary of filename -> file content
            workspace: Path to temporary workspace directory

        Returns:
            AnalyzerResult: Analysis results
        """
        pass

    def _map_severity(self, tool_severity: str) -> str:
        """
        Map tool-specific severity to our standard levels.

        Args:
            tool_severity: Severity from analysis tool

        Returns:
            str: Normalized severity (critical, warning, info)
        """
        # Default mapping, override in subclasses
        severity_map = {
            "HIGH": "critical",
            "MEDIUM": "warning",
            "LOW": "info",
            "ERROR": "critical",
            "WARNING": "warning",
            "INFO": "info",
        }
        return severity_map.get(tool_severity.upper(), "info")


def extract_python_files_from_diff(diff_content: str) -> Dict[str, str]:
    """
    Extract Python file paths and content from a git diff.

    Args:
        diff_content: Git diff string

    Returns:
        Dict[str, str]: Dictionary of filename -> file content
    """
    files = {}
    current_file = None
    current_content = []

    for line in diff_content.split("\n"):
        if line.startswith("diff --git"):
            # Save previous file
            if current_file and current_content:
                files[current_file] = "\n".join(current_content)
                current_content = []

            # Extract filename
            parts = line.split(" ")
            if len(parts) >= 4:
                filepath = parts[3][2:]  # Remove 'b/' prefix
                if filepath.endswith(".py"):
                    current_file = filepath
                else:
                    current_file = None

        elif current_file and line.startswith("+") and not line.startswith("+++"):
            # This is an added line (excluding file header)
            current_content.append(line[1:])  # Remove '+' prefix

    # Save last file
    if current_file and current_content:
        files[current_file] = "\n".join(current_content)

    return files


def create_temp_workspace() -> Path:
    """
    Create a temporary workspace directory for analysis.

    Returns:
        Path: Path to temporary directory
    """
    temp_dir = tempfile.mkdtemp(prefix="code_review_")
    return Path(temp_dir)


def cleanup_workspace(workspace: Path):
    """
    Clean up temporary workspace directory.

    Args:
        workspace: Path to workspace directory
    """
    if workspace.exists() and workspace.is_dir():
        shutil.rmtree(workspace)


def write_files_to_workspace(files: Dict[str, str], workspace: Path):
    """
    Write code files to workspace directory.

    Args:
        files: Dictionary of filename -> content
        workspace: Path to workspace directory
    """
    for filepath, content in files.items():
        full_path = workspace / filepath

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Filename or path

    Returns:
        str: File extension (e.g., '.py')
    """
    return Path(filename).suffix
