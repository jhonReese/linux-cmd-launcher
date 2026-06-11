"""
Unit tests for CommandLibrary.
Run with:  python3 -m pytest tests/ -v
"""
import json
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.core.commands import CommandLibrary


SAMPLE_CONFIG = {
    "version": "1.0.0",
    "categories": [
        {
            "name": "Test Category",
            "color": "#AABBCC",
            "commands": [
                {"cmd": "htop",              "desc": "Interactive process viewer"},
                {"cmd": "git log --oneline", "desc": "Compact git history"},
                {"cmd": "jq '.k' f.json",    "desc": "Parse JSON field"},
                {"cmd": "docker ps -a",      "desc": "List all containers"},
            ],
        }
    ],
}


@pytest.fixture
def lib(tmp_path):
    cfg = tmp_path / "commands.json"
    cfg.write_text(json.dumps(SAMPLE_CONFIG))
    hist = tmp_path / "history.json"

    instance = CommandLibrary.__new__(CommandLibrary)
    instance._config_path  = cfg
    instance._history_path = hist
    instance._data         = {}
    instance._history      = []
    instance.load()
    instance._load_history()
    return instance


class TestLoad:
    def test_categories_loaded(self, lib):
        assert len(lib.categories) == 1

    def test_command_count(self, lib):
        assert len(lib.categories[0]["commands"]) == 4

    def test_malformed_json_returns_empty(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")
        instance = CommandLibrary.__new__(CommandLibrary)
        instance._config_path  = bad
        instance._history_path = tmp_path / "history.json"
        instance._data         = {}
        instance._history      = []
        instance.load()
        assert instance.categories == []


class TestSearch:
    def test_exact_cmd_match(self, lib):
        results = lib.search("htop")
        assert len(results) == 1
        assert results[0]["cmd"] == "htop"

    def test_exact_desc_match(self, lib):
        results = lib.search("process")
        assert any(r["cmd"] == "htop" for r in results)

    def test_cmd_ranks_above_desc(self, lib):
        # "git" hits cmd "git log --oneline" directly (score 2)
        results = lib.search("git")
        assert results[0]["cmd"] == "git log --oneline"
        assert results[0]["score"] >= 2.0

    def test_multiword_all_tokens_match(self, lib):
        results = lib.search("git log")
        assert len(results) == 1
        assert results[0]["cmd"] == "git log --oneline"

    def test_multiword_partial_no_match(self, lib):
        # "git xyz" — "git" matches but "xyz" doesn't → 0 results
        assert lib.search("git xyz") == []

    def test_fuzzy_typo_match(self, lib):
        # "htpo" is a transposition of "htop" — fuzzy should catch it
        results = lib.search("htpo")
        assert any(r["cmd"] == "htop" for r in results)

    def test_empty_query_returns_empty(self, lib):
        assert lib.search("") == []

    def test_whitespace_only_returns_empty(self, lib):
        assert lib.search("   ") == []

    def test_no_match_returns_empty(self, lib):
        assert lib.search("zzzznotexist") == []

    def test_results_sorted_descending(self, lib):
        results = lib.search("docker")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_result_includes_category_and_color(self, lib):
        results = lib.search("htop")
        assert results[0]["category"] == "Test Category"
        assert results[0]["color"]    == "#AABBCC"


class TestRecordUse:
    def test_record_adds_to_history(self, lib):
        lib.record_use("htop")
        assert lib.recent[0]["cmd"] == "htop"

    def test_record_deduplicates(self, lib):
        lib.record_use("htop")
        lib.record_use("htop")
        assert sum(1 for h in lib.recent if h["cmd"] == "htop") == 1

    def test_record_moves_to_top(self, lib):
        lib.record_use("git log --oneline")
        lib.record_use("htop")
        lib.record_use("git log --oneline")
        assert lib.recent[0]["cmd"] == "git log --oneline"

    def test_history_capped_at_20(self, lib):
        for i in range(25):
            lib.record_use(f"cmd-{i}")
        assert len(lib._history) == 20

    def test_recent_returns_max_8(self, lib):
        for i in range(15):
            lib.record_use(f"cmd-{i}")
        assert len(lib.recent) == 8
