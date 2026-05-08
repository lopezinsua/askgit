"""Tests for askgit agent utilities."""
import pytest
from unittest.mock import MagicMock

from agent import parse_repo_url, tool_label


def test_parse_valid_url():
    owner, repo = parse_repo_url("https://github.com/octocat/hello-world")
    assert owner == "octocat"
    assert repo == "hello-world"


def test_parse_strips_git_suffix():
    owner, repo = parse_repo_url("https://github.com/octocat/hello-world.git")
    assert repo == "hello-world"


def test_parse_invalid_chars():
    with pytest.raises(SystemExit):
        parse_repo_url("https://github.com/oc../repo")


def test_parse_too_short():
    with pytest.raises(SystemExit):
        parse_repo_url("https://github.com/onlyone")


def test_tool_label_read_file():
    label = tool_label("read_file", {"path": "src/main.py"})
    assert "src/main.py" in label


def test_tool_label_list_files():
    label = tool_label("list_files", {"path": "src/"})
    assert "src/" in label


def test_tool_label_search_code():
    label = tool_label("search_code", {"query": "import os"})
    assert "import os" in label


def test_tool_label_fallback():
    label = tool_label("get_repo_info", {})
    assert label
