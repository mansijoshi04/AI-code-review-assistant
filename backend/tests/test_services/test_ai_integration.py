"""
Tests for AI integration (Claude service and AI reviewer).
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.services.claude_service import ClaudeService
from app.services.analysis.ai_reviewer import AIReviewer
from pathlib import Path


class TestClaudeService:
    """Tests for Claude API service."""

    def test_service_initialization(self):
        """Test Claude service initializes correctly."""
        service = ClaudeService()
        assert service.model == "claude-3-5-sonnet-20241022"
        assert service.max_tokens == 4096
        assert service.temperature == 0.0

    @patch("app.services.claude_service.settings.ANTHROPIC_API_KEY", "")
    def test_is_available_without_api_key(self):
        """Test service reports unavailable when API key is missing."""
        service = ClaudeService()
        assert service.is_available() is False

    @patch("app.services.claude_service.settings.ANTHROPIC_API_KEY", "test-key")
    def test_is_available_with_api_key(self):
        """Test service reports available when API key is present."""
        service = ClaudeService()
        assert service.is_available() is True

    @pytest.mark.asyncio
    @patch("app.services.claude_service.settings.ANTHROPIC_API_KEY", "")
    async def test_review_code_without_api_key(self):
        """Test review code raises error without API key."""
        service = ClaudeService()
        files = {"test.py": "print('hello')"}

        with pytest.raises(Exception, match="Claude API key not configured"):
            await service.review_code(files)

    def test_build_review_prompt(self):
        """Test review prompt construction."""
        service = ClaudeService()
        files = {"app/main.py": "def hello():\n    print('world')"}
        pr_context = {"title": "Test PR", "description": "Test description"}

        prompt = service._build_review_prompt(files, pr_context)

        assert "Test PR" in prompt
        assert "Test description" in prompt
        assert "app/main.py" in prompt
        assert "def hello():" in prompt
        assert "best-practices" in prompt
        assert "JSON format" in prompt

    def test_build_review_prompt_without_context(self):
        """Test review prompt without PR context."""
        service = ClaudeService()
        files = {"test.py": "x = 1"}

        prompt = service._build_review_prompt(files, None)

        assert "test.py" in prompt
        assert "x = 1" in prompt
        assert "Pull Request Context" not in prompt

    @pytest.mark.asyncio
    @patch("app.services.claude_service.settings.ANTHROPIC_API_KEY", "test-key")
    @patch("app.services.claude_service.anthropic.Anthropic")
    async def test_review_code_success(self, mock_anthropic_class):
        """Test successful code review call."""
        # Mock the Anthropic client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_text_block = Mock()
        mock_text_block.type = "text"
        mock_text_block.text = '{"findings": [], "summary": "Code looks good"}'
        mock_response.content = [mock_text_block]

        mock_client.messages.create.return_value = mock_response

        service = ClaudeService()
        files = {"test.py": "print('hello')"}

        result = await service.review_code(files)

        assert "Code looks good" in result
        mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.claude_service.settings.ANTHROPIC_API_KEY", "test-key")
    @patch("app.services.claude_service.anthropic.Anthropic")
    async def test_review_code_api_error(self, mock_anthropic_class):
        """Test code review handles API errors."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Simulate API error
        mock_client.messages.create.side_effect = Exception("API error")

        service = ClaudeService()
        files = {"test.py": "print('hello')"}

        with pytest.raises(Exception, match="Claude API call failed"):
            await service.review_code(files)


class TestAIReviewer:
    """Tests for AI reviewer analyzer."""

    def test_ai_reviewer_initialization(self):
        """Test AI reviewer initializes correctly."""
        reviewer = AIReviewer()
        assert reviewer.name == "AI Reviewer"

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_without_api_key(self, mock_service):
        """Test analyze returns error when API key not configured."""
        mock_service.is_available.return_value = False

        reviewer = AIReviewer()
        files = {"test.py": "print('hello')"}
        workspace = Path("/tmp/test")

        result = await reviewer.analyze(files, workspace)

        assert result.success is False
        assert "Claude API key not configured" in result.error
        assert len(result.findings) == 0

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_success(self, mock_service):
        """Test successful AI analysis."""
        mock_service.is_available.return_value = True
        mock_service.review_code = AsyncMock(return_value='''
```json
{
  "findings": [
    {
      "category": "best-practices",
      "severity": "warning",
      "title": "Use type hints",
      "description": "Function lacks type hints",
      "file_path": "test.py",
      "line_number": 1,
      "code_snippet": "def hello():",
      "suggestion": "Add type hints: def hello() -> None:"
    }
  ],
  "summary": "Good code overall, minor improvements needed"
}
```
        ''')

        reviewer = AIReviewer()
        files = {"test.py": "def hello():\n    print('world')"}
        workspace = Path("/tmp/test")

        result = await reviewer.analyze(files, workspace)

        assert result.success is True
        assert len(result.findings) == 1
        assert result.findings[0]["title"] == "Use type hints"
        assert result.findings[0]["severity"] == "warning"
        assert result.findings[0]["tool_source"] == "ai-claude"

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_with_pr_context(self, mock_service):
        """Test analysis includes PR context."""
        mock_service.is_available.return_value = True
        mock_service.review_code = AsyncMock(return_value='{"findings": [], "summary": "OK"}')

        reviewer = AIReviewer()
        files = {"test.py": "x = 1"}
        workspace = Path("/tmp/test")
        pr_context = {"title": "Fix bug", "description": "Fixes issue #123"}

        result = await reviewer.analyze(files, workspace, pr_context)

        # Verify PR context was passed
        mock_service.review_code.assert_called_once()
        call_args = mock_service.review_code.call_args
        assert call_args[1]["pr_context"] == pr_context

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_handles_api_error(self, mock_service):
        """Test analysis handles API errors gracefully."""
        mock_service.is_available.return_value = True
        mock_service.review_code = AsyncMock(side_effect=Exception("API error"))

        reviewer = AIReviewer()
        files = {"test.py": "print('hello')"}
        workspace = Path("/tmp/test")

        result = await reviewer.analyze(files, workspace)

        assert result.success is False
        assert "AI review failed" in result.error
        assert len(result.findings) == 0

    def test_truncate_files_small(self):
        """Test file truncation with small files."""
        reviewer = AIReviewer()
        files = {
            "file1.py": "a" * 100,
            "file2.py": "b" * 200,
            "file3.py": "c" * 150,
        }

        truncated = reviewer._truncate_files(files, max_chars=500)

        assert len(truncated) == 3
        assert "file1.py" in truncated
        assert "file2.py" in truncated
        assert "file3.py" in truncated

    def test_truncate_files_large(self):
        """Test file truncation with large files."""
        reviewer = AIReviewer()
        files = {
            "small.py": "a" * 100,
            "medium.py": "b" * 1000,
            "large.py": "c" * 50000,
        }

        truncated = reviewer._truncate_files(files, max_chars=2000)

        # Should include small and medium, but not large
        assert "small.py" in truncated
        assert "medium.py" in truncated
        # Large file might be truncated or excluded
        total_size = sum(len(content) for content in truncated.values())
        assert total_size <= 2000

    def test_parse_ai_response_json_in_markdown(self):
        """Test parsing JSON response wrapped in markdown."""
        reviewer = AIReviewer()
        response = '''
Here's my review:

```json
{
  "findings": [
    {
      "category": "performance",
      "severity": "critical",
      "title": "Inefficient loop",
      "description": "Loop can be optimized",
      "file_path": "app.py",
      "line_number": 42,
      "suggestion": "Use list comprehension"
    }
  ],
  "summary": "Needs optimization"
}
```
        '''

        findings = reviewer._parse_ai_response(response)

        assert len(findings) == 1
        assert findings[0]["title"] == "Inefficient loop"
        assert findings[0]["severity"] == "critical"
        assert findings[0]["category"] == "performance"

    def test_parse_ai_response_plain_json(self):
        """Test parsing plain JSON response."""
        reviewer = AIReviewer()
        response = '{"findings": [{"category": "testing", "severity": "info", "title": "Add tests"}], "summary": "OK"}'

        findings = reviewer._parse_ai_response(response)

        assert len(findings) == 1
        assert findings[0]["title"] == "Add tests"

    def test_parse_ai_response_invalid_json(self):
        """Test parsing invalid JSON falls back to text."""
        reviewer = AIReviewer()
        response = "This is just text feedback about the code"

        findings = reviewer._parse_ai_response(response)

        # Should create a generic finding from the text
        assert len(findings) == 1
        assert findings[0]["category"] == "ai-review"
        assert findings[0]["severity"] == "info"
        assert "text feedback" in findings[0]["description"]

    def test_parse_ai_response_invalid_severity(self):
        """Test parsing normalizes invalid severity values."""
        reviewer = AIReviewer()
        response = '''
```json
{
  "findings": [
    {
      "category": "quality",
      "severity": "SUPER_CRITICAL",
      "title": "Bad code"
    }
  ]
}
```
        '''

        findings = reviewer._parse_ai_response(response)

        assert len(findings) == 1
        assert findings[0]["severity"] == "info"  # Falls back to info

    def test_map_category(self):
        """Test category mapping."""
        reviewer = AIReviewer()

        assert reviewer._map_category("best-practices") == "best-practices"
        assert reviewer._map_category("design") == "design"
        assert reviewer._map_category("performance") == "performance"
        assert reviewer._map_category("unknown-category") == "ai-review"
        assert reviewer._map_category("SECURITY") == "security"  # Case insensitive

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_empty_files(self, mock_service):
        """Test analysis with empty files dict."""
        mock_service.is_available.return_value = True

        reviewer = AIReviewer()
        files = {}
        workspace = Path("/tmp/test")

        result = await reviewer.analyze(files, workspace)

        assert result.success is True
        assert len(result.findings) == 0
        # Should not call API with empty files
        mock_service.review_code.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.services.analysis.ai_reviewer.claude_service")
    async def test_analyze_multiple_findings(self, mock_service):
        """Test analysis with multiple findings."""
        mock_service.is_available.return_value = True
        mock_service.review_code = AsyncMock(return_value='''
```json
{
  "findings": [
    {
      "category": "security",
      "severity": "critical",
      "title": "SQL Injection",
      "description": "Unsafe query",
      "file_path": "db.py",
      "line_number": 10
    },
    {
      "category": "best-practices",
      "severity": "warning",
      "title": "Use constants",
      "description": "Magic numbers",
      "file_path": "config.py",
      "line_number": 5
    },
    {
      "category": "testing",
      "severity": "info",
      "title": "Add unit tests",
      "description": "No tests found",
      "file_path": "service.py"
    }
  ],
  "summary": "Multiple issues found"
}
```
        ''')

        reviewer = AIReviewer()
        files = {"test.py": "code"}
        workspace = Path("/tmp/test")

        result = await reviewer.analyze(files, workspace)

        assert result.success is True
        assert len(result.findings) == 3

        # Verify findings are properly parsed
        severities = [f["severity"] for f in result.findings]
        assert "critical" in severities
        assert "warning" in severities
        assert "info" in severities
