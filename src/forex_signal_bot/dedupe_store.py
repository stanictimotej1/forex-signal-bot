from __future__ import annotations

import json
from pathlib import Path


class SignalStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps({"signals": []}, indent=2), encoding="utf-8")

    def _load(self) -> dict:
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def _save(self, payload: dict) -> None:
        self.file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def has(self, key: str) -> bool:
        payload = self._load()
        return key in payload.get("signals", [])

    def add(self, key: str) -> None:
        payload = self._load()
        signals = payload.setdefault("signals", [])
        if key not in signals:
            signals.append(key)
            self._save(payload)
