#!/usr/bin/env python3
"""Unit tests for installer module."""

import json
import urllib.error
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest

from zsh_llm_suggestions.installer import (
    compare_versions,
    get_latest_github_release,
    parse_version,
)


class TestParseVersion:
    """Test version string parsing."""

    def test_parse_version_with_v_prefix(self) -> None:
        """Test parsing version with 'v' prefix."""
        result = parse_version("v0.3.1")
        assert result == (0, 3, 1)

    def test_parse_version_without_v_prefix(self) -> None:
        """Test parsing version without 'v' prefix."""
        result = parse_version("0.3.1")
        assert result == (0, 3, 1)

    def test_parse_version_major_minor_only(self) -> None:
        """Test parsing version with only major and minor."""
        result = parse_version("1.0")
        assert result == (1, 0)

    def test_parse_version_four_parts(self) -> None:
        """Test parsing version with four parts."""
        result = parse_version("1.2.3.4")
        assert result == (1, 2, 3, 4)

    def test_parse_version_invalid_empty(self) -> None:
        """Test parsing empty version string."""
        result = parse_version("")
        assert result is None

    def test_parse_version_invalid_non_numeric(self) -> None:
        """Test parsing version with non-numeric parts."""
        result = parse_version("v1.2.beta")
        assert result is None

    def test_parse_version_invalid_none(self) -> None:
        """Test parsing None value."""
        result = parse_version(None)  # type: ignore[arg-type]
        assert result is None


class TestGetLatestGithubRelease:
    """Test GitHub API release fetching."""

    @patch("urllib.request.urlopen")
    def test_successful_fetch(self, mock_urlopen: MagicMock) -> None:
        """Test successful fetch of latest release."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"tag_name": "v0.3.2"}).encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = get_latest_github_release()
        assert result == "v0.3.2"

    @patch("urllib.request.urlopen")
    def test_network_error(self, mock_urlopen: MagicMock) -> None:
        """Test handling of network errors."""
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")

        result = get_latest_github_release()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_timeout_error(self, mock_urlopen: MagicMock) -> None:
        """Test handling of timeout errors."""
        mock_urlopen.side_effect = TimeoutError("Connection timed out")

        result = get_latest_github_release()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen: MagicMock) -> None:
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = get_latest_github_release()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_missing_tag_name(self, mock_urlopen: MagicMock) -> None:
        """Test handling of response missing tag_name field."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"other_field": "value"}).encode()
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = get_latest_github_release()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_api_rate_limit(self, mock_urlopen: MagicMock) -> None:
        """Test handling of GitHub API rate limit."""
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/...",
            403,
            "Forbidden",
            {},
            None,  # type: ignore[arg-type]
        )

        result = get_latest_github_release()
        assert result is None


class TestCompareVersions:
    """Test version comparison logic."""

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    @patch("zsh_llm_suggestions.installer.__version__", "0.3.0")
    def test_update_available(self, mock_get_latest: MagicMock) -> None:
        """Test detection of available update."""
        mock_get_latest.return_value = "v0.3.2"

        is_update_available, latest_version = compare_versions()
        assert is_update_available is True
        assert latest_version == "v0.3.2"

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    @patch("zsh_llm_suggestions.installer.__version__", "0.3.2")
    def test_up_to_date(self, mock_get_latest: MagicMock) -> None:
        """Test when current version is up to date."""
        mock_get_latest.return_value = "v0.3.2"

        is_update_available, latest_version = compare_versions()
        assert is_update_available is False
        assert latest_version == "v0.3.2"

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    @patch("zsh_llm_suggestions.installer.__version__", "0.4.0")
    def test_ahead_of_latest(self, mock_get_latest: MagicMock) -> None:
        """Test when current version is ahead of latest release."""
        mock_get_latest.return_value = "v0.3.2"

        is_update_available, latest_version = compare_versions()
        assert is_update_available is False
        assert latest_version == "v0.3.2"

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    def test_network_error(self, mock_get_latest: MagicMock) -> None:
        """Test handling when GitHub API is unreachable."""
        mock_get_latest.return_value = None

        is_update_available, latest_version = compare_versions()
        assert is_update_available is False
        assert latest_version is None

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    @patch("zsh_llm_suggestions.installer.__version__", "invalid")
    def test_invalid_current_version(self, mock_get_latest: MagicMock) -> None:
        """Test handling of invalid current version."""
        mock_get_latest.return_value = "v0.3.2"

        is_update_available, latest_version = compare_versions()
        assert is_update_available is False
        assert latest_version == "v0.3.2"

    @patch("zsh_llm_suggestions.installer.get_latest_github_release")
    @patch("zsh_llm_suggestions.installer.__version__", "0.3.0")
    def test_invalid_latest_version(self, mock_get_latest: MagicMock) -> None:
        """Test handling of invalid latest version from API."""
        mock_get_latest.return_value = "invalid-version"

        is_update_available, latest_version = compare_versions()
        assert is_update_available is False
        assert latest_version == "invalid-version"
