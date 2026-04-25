"""Tests for utility functions: esc(), make_header(), get_version(), write_pack()."""
import os
import re
import subprocess
from unittest.mock import MagicMock, patch

import pytest

import generate_espanso as ge

# ---------------------------------------------------------------------------
# esc()
# ---------------------------------------------------------------------------

class TestEsc:
    def test_wraps_plain_string_in_double_quotes(self):
        assert ge.esc("test") == '"test"'

    def test_wraps_empty_string(self):
        assert ge.esc("") == '""'

    def test_wraps_string_with_spaces(self):
        assert ge.esc("hello world") == '"hello world"'

    def test_wraps_string_with_accent(self):
        assert ge.esc("perché") == '"perché"'

    def test_wraps_string_with_apostrophe(self):
        result = ge.esc("e'")
        assert result.startswith('"')
        assert result.endswith('"')
        assert "e'" in result


# ---------------------------------------------------------------------------
# make_header()
# ---------------------------------------------------------------------------

class TestMakeHeader:
    def test_returns_list(self):
        header = ge.make_header("Italiano", "Everyday words")
        assert isinstance(header, list)

    def test_contains_title(self):
        header = ge.make_header("Italiano", "Everyday words")
        combined = "\n".join(header)
        assert "Italiano" in combined

    def test_contains_description(self):
        header = ge.make_header("Test", "My description")
        combined = "\n".join(header)
        assert "My description" in combined

    def test_contains_github_url(self):
        header = ge.make_header("Test", "Desc")
        combined = "\n".join(header)
        assert "https://github.com/heavybeard/refuos" in combined

    def test_penultimate_element_is_matches(self):
        header = ge.make_header("Test", "Desc")
        assert header[-2] == "matches:"

    def test_last_element_is_empty_string(self):
        header = ge.make_header("Test", "Desc")
        assert header[-1] == ""


# ---------------------------------------------------------------------------
# get_version()
# ---------------------------------------------------------------------------

class TestGetVersion:
    def test_returns_string(self):
        version = ge.get_version()
        assert isinstance(version, str)

    def test_version_matches_semver_pattern(self):
        version = ge.get_version()
        assert re.match(r"^\d+\.\d+\.\d+$", version), (
            f"Version '{version}' does not match X.Y.Z pattern"
        )

    def test_fallback_when_git_fails(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        with patch("subprocess.run", return_value=mock_result):
            version = ge.get_version()
        assert version == "0.1.0"

    def test_fallback_when_git_not_found(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            version = ge.get_version()
        assert version == "0.1.0"

    def test_fallback_when_git_times_out(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            version = ge.get_version()
        assert version == "0.1.0"

    def test_strips_leading_v_from_tag(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "v1.2.3\n"
        with patch("subprocess.run", return_value=mock_result):
            version = ge.get_version()
        assert version == "1.2.3"

    def test_handles_tag_without_v_prefix(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "2.0.0\n"
        with patch("subprocess.run", return_value=mock_result):
            version = ge.get_version()
        assert version == "2.0.0"


# ---------------------------------------------------------------------------
# write_pack()
# ---------------------------------------------------------------------------

class TestWritePack:
    def test_creates_file_with_correct_content(self, tmp_path):
        content = "# header\nmatches:\n\n  - trigger: \"acnhe\"\n    replace: \"anche\"\n"
        ge.write_pack(str(tmp_path), "test.yml", content, 1)
        written = (tmp_path / "test.yml").read_text(encoding="utf-8")
        assert written == content

    def test_returns_total(self, tmp_path):
        result = ge.write_pack(str(tmp_path), "test.yml", "content\n", 42)
        assert result == 42

    def test_output_dir_is_used(self, tmp_path):
        ge.write_pack(str(tmp_path), "output.yml", "content\n", 0)
        assert (tmp_path / "output.yml").exists()

    def test_prints_summary(self, tmp_path, capsys):
        ge.write_pack(str(tmp_path), "test.yml", "content\n", 99)
        captured = capsys.readouterr()
        assert "test.yml" in captured.out
        assert "99" in captured.out
