from __future__ import annotations

import json
from pathlib import Path


class HighScoreManager:
    """
    Менеджер таблицы рекордов.
    Хранит данные в JSON.
    """

    def __init__(self, file_path: str | Path, max_scores: int = 10) -> None:
        self.file_path = Path(file_path)
        self.max_scores = max_scores

        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_data({"scores": []})

    def _read_data(self) -> dict:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {"scores": []}

        if not isinstance(data, dict):
            data = {"scores": []}

        if "scores" not in data or not isinstance(data["scores"], list):
            data["scores"] = []

        return data

    def _write_data(self, data: dict) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def get_scores(self) -> list[dict]:
        data = self._read_data()
        scores = data["scores"]

        valid_scores: list[dict] = []
        for entry in scores:
            if not isinstance(entry, dict):
                continue

            score = int(entry.get("score", 0))
            wave = int(entry.get("wave", 0))
            name = str(entry.get("name", "PLAYER"))

            valid_scores.append(
                {
                    "name": name,
                    "score": score,
                    "wave": wave,
                }
            )

        valid_scores.sort(key=lambda item: item["score"], reverse=True)
        return valid_scores[: self.max_scores]

    def add_score(self, score: int, wave: int, name: str = "PLAYER") -> None:
        scores = self.get_scores()
        scores.append(
            {
                "name": name,
                "score": int(score),
                "wave": int(wave),
            }
        )
        scores.sort(key=lambda item: item["score"], reverse=True)
        scores = scores[: self.max_scores]

        self._write_data({"scores": scores})

    def is_top_score(self, score: int) -> bool:
        scores = self.get_scores()
        if not scores:
            return True
        return score > scores[0]["score"]