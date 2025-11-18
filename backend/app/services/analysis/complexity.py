"""
Code complexity analyzer using Radon.
"""

import json
import subprocess
from typing import Dict, List, Any
from pathlib import Path
from app.services.analysis.base import BaseAnalyzer, AnalyzerResult


class ComplexityAnalyzer(BaseAnalyzer):
    """Code complexity analyzer using Radon."""

    def __init__(self):
        """Initialize complexity analyzer."""
        super().__init__("complexity")
        self.complexity_thresholds = {
            "A": (1, 5),  # Low risk
            "B": (6, 10),  # Moderate risk
            "C": (11, 20),  # High risk
            "D": (21, 30),  # Very high risk
            "F": (31, float("inf")),  # Extreme risk
        }

    async def analyze(self, files: Dict[str, str], workspace: Path) -> AnalyzerResult:
        """
        Run Radon complexity analysis on Python files.

        Args:
            files: Dictionary of filename -> content
            workspace: Path to workspace directory

        Returns:
            AnalyzerResult: Complexity analysis results
        """
        findings = []

        try:
            # Run Radon cyclomatic complexity
            cc_findings = await self._analyze_cyclomatic_complexity(workspace)
            findings.extend(cc_findings)

            # Run Radon maintainability index
            mi_findings = await self._analyze_maintainability(workspace)
            findings.extend(mi_findings)

            return AnalyzerResult(tool="radon", findings=findings, success=True)

        except Exception as e:
            return AnalyzerResult(
                tool="radon", findings=[], success=False, error=str(e)
            )

    async def _analyze_cyclomatic_complexity(
        self, workspace: Path
    ) -> List[Dict[str, Any]]:
        """
        Analyze cyclomatic complexity with Radon.

        Args:
            workspace: Path to workspace directory

        Returns:
            List[Dict[str, Any]]: Complexity findings
        """
        try:
            result = subprocess.run(
                [
                    "radon",
                    "cc",
                    str(workspace),
                    "-j",  # JSON output
                    "-n",
                    "C",  # Show C grade and above (complexity >= 11)
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                radon_data = json.loads(result.stdout)
                return self._parse_complexity_output(radon_data, workspace)

            return []

        except subprocess.TimeoutExpired:
            return []
        except json.JSONDecodeError:
            return []
        except Exception:
            return []

    async def _analyze_maintainability(self, workspace: Path) -> List[Dict[str, Any]]:
        """
        Analyze maintainability index with Radon.

        Args:
            workspace: Path to workspace directory

        Returns:
            List[Dict[str, Any]]: Maintainability findings
        """
        try:
            result = subprocess.run(
                [
                    "radon",
                    "mi",
                    str(workspace),
                    "-j",  # JSON output
                    "-n",
                    "B",  # Show B grade and below (MI < 65)
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                radon_data = json.loads(result.stdout)
                return self._parse_maintainability_output(radon_data, workspace)

            return []

        except subprocess.TimeoutExpired:
            return []
        except json.JSONDecodeError:
            return []
        except Exception:
            return []

    def _parse_complexity_output(
        self, radon_data: Dict[str, Any], workspace: Path
    ) -> List[Dict[str, Any]]:
        """
        Parse Radon cyclomatic complexity JSON output.

        Args:
            radon_data: Parsed JSON from Radon
            workspace: Workspace path for relative path calculation

        Returns:
            List[Dict[str, Any]]: List of finding dictionaries
        """
        findings = []

        for file_path, functions in radon_data.items():
            # Get relative path from workspace
            rel_path = Path(file_path).relative_to(workspace)

            for func in functions:
                complexity = func.get("complexity", 0)
                rank = func.get("rank", "A")

                # Determine severity based on complexity
                if complexity >= 21:
                    severity = "critical"
                elif complexity >= 11:
                    severity = "warning"
                else:
                    severity = "info"

                # Generate suggestion
                if complexity >= 21:
                    suggestion = "This function is extremely complex. Consider breaking it into smaller, focused functions."
                elif complexity >= 11:
                    suggestion = "This function is moderately complex. Consider refactoring to improve readability."
                else:
                    suggestion = "This function has acceptable complexity."

                finding = {
                    "category": "complexity",
                    "severity": severity,
                    "title": f"High cyclomatic complexity in {func.get('name', 'function')}",
                    "description": f"Function '{func.get('name', 'unknown')}' has cyclomatic complexity of {complexity} (rank {rank})",
                    "file_path": str(rel_path),
                    "line_number": func.get("lineno", 0),
                    "code_snippet": "",
                    "suggestion": suggestion,
                    "tool_source": "radon",
                    "complexity_score": complexity,
                    "complexity_rank": rank,
                }

                findings.append(finding)

        return findings

    def _parse_maintainability_output(
        self, radon_data: Dict[str, Any], workspace: Path
    ) -> List[Dict[str, Any]]:
        """
        Parse Radon maintainability index JSON output.

        Args:
            radon_data: Parsed JSON from Radon
            workspace: Workspace path for relative path calculation

        Returns:
            List[Dict[str, Any]]: List of finding dictionaries
        """
        findings = []

        for file_path, data in radon_data.items():
            # Get relative path from workspace
            rel_path = Path(file_path).relative_to(workspace)

            mi = data.get("mi", 100)
            rank = data.get("rank", "A")

            # Determine severity based on maintainability index
            # A: 80-100, B: 65-79, C: 50-64, D: 25-49, F: 0-24
            if mi < 25:
                severity = "critical"
            elif mi < 50:
                severity = "warning"
            elif mi < 65:
                severity = "info"
            else:
                continue  # Skip high maintainability files

            # Generate suggestion
            if mi < 25:
                suggestion = "This file has very low maintainability. Major refactoring recommended."
            elif mi < 50:
                suggestion = "This file has low maintainability. Consider refactoring to improve code quality."
            else:
                suggestion = "This file has moderate maintainability. Minor improvements recommended."

            finding = {
                "category": "maintainability",
                "severity": severity,
                "title": f"Low maintainability index in {rel_path.name}",
                "description": f"File has maintainability index of {mi:.2f} (rank {rank})",
                "file_path": str(rel_path),
                "line_number": 1,
                "code_snippet": "",
                "suggestion": suggestion,
                "tool_source": "radon",
                "maintainability_index": mi,
                "maintainability_rank": rank,
            }

            findings.append(finding)

        return findings


# Global complexity analyzer instance
complexity_analyzer = ComplexityAnalyzer()
