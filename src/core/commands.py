"""
指令庫管理：JSON 讀取、全文搜尋、最近使用記錄
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class CommandLibrary:
    def __init__(self):
        self._config_path  = self._resolve_config()
        self._history_path = Path.home() / ".config" / "cmd-launcher" / "history.json"
        self._data: Dict   = {}
        self._history: List[Dict] = []
        self.load()
        self._load_history()

    def _resolve_config(self) -> Path:
        user = Path.home() / ".config" / "cmd-launcher" / "commands.json"
        if user.exists():
            return user
        return Path(__file__).parent.parent.parent / "config" / "commands.json"

    def load(self):
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {"categories": []}

    def _load_history(self):
        try:
            if self._history_path.exists():
                with open(self._history_path, "r") as f:
                    self._history = json.load(f)
        except Exception:
            self._history = []

    def record_use(self, cmd: str):
        """記錄最近使用的指令（最多保留 20 筆）"""
        self._history = [h for h in self._history if h["cmd"] != cmd]
        self._history.insert(0, {"cmd": cmd, "time": datetime.now().isoformat()})
        self._history = self._history[:20]
        try:
            self._history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._history_path, "w") as f:
                json.dump(self._history, f, indent=2)
        except Exception:
            pass

    @property
    def categories(self) -> List[Dict]:
        return self._data.get("categories", [])

    @property
    def recent(self) -> List[Dict]:
        return self._history[:8]

    def search(self, query: str) -> List[Dict]:
        import difflib
        q = query.strip()
        if not q:
            return []
        tokens = q.lower().split()
        results = []
        for cat in self.categories:
            for item in cat.get("commands", []):
                cmd_lower  = item["cmd"].lower()
                desc_lower = item["desc"].lower()
                score: float = 0.0

                # Substring scoring per token
                for token in tokens:
                    if token in cmd_lower:
                        score += 2.0
                    elif token in desc_lower:
                        score += 1.0

                # Multi-word: all tokens must match somewhere
                if len(tokens) > 1:
                    if not all(
                        t in cmd_lower or t in desc_lower for t in tokens
                    ):
                        score = 0.0

                # Fuzzy fallback when no substring hit
                if score == 0.0:
                    combined = cmd_lower + " " + desc_lower
                    ratio = difflib.SequenceMatcher(
                        None, q.lower(), combined
                    ).ratio()
                    if ratio > 0.45:
                        score = ratio  # float < 1.0, always ranks below exact hits

                if score > 0.0:
                    results.append({
                        **item,
                        "category": cat["name"],
                        "color":    cat.get("color", "#888888"),
                        "score":    score,
                    })
        return sorted(results, key=lambda x: x["score"], reverse=True)
