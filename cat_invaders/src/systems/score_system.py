from __future__ import annotations


class ScoreSystem:
    """
    Система очков.
    Хранит текущий счёт и реагирует на уничтожение врагов.
    """

    def __init__(self, game) -> None:
        self.game = game
        self.score = 0
        self.high_score = 0

        self.game.event_bus.subscribe("enemy_destroyed", self.on_enemy_destroyed)
        self.game.event_bus.subscribe("boss_destroyed", self.on_boss_destroyed)

    def on_enemy_destroyed(self, enemy, score: int = 0, **kwargs) -> None:
        self.add_score(score)

    def on_boss_destroyed(self, boss, score: int = 0, **kwargs) -> None:
        self.add_score(score)

    def add_score(self, amount: int) -> None:
        self.score += int(amount)
        if self.score > self.high_score:
            self.high_score = self.score

        self.game.event_bus.emit(
            "score_changed",
            score=self.score,
            high_score=self.high_score,
        )

    def reset(self) -> None:
        self.score = 0
        self.game.event_bus.emit(
            "score_changed",
            score=self.score,
            high_score=self.high_score,
        )

    def shutdown(self) -> None:
        self.game.event_bus.unsubscribe("enemy_destroyed", self.on_enemy_destroyed)
        self.game.event_bus.unsubscribe("boss_destroyed", self.on_boss_destroyed)