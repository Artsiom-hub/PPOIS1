from __future__ import annotations

import pygame

from src.core.scene_manager import BaseScene


class HelpScene(BaseScene):
    def on_enter(self, **kwargs) -> None:
        self.font = pygame.font.Font(None, 34)
        self.title_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 28)

        self.lines = [
            "УПРАВЛЕНИЕ:",
            "LEFT / RIGHT или A / D - движение",
            "SPACE - стрельба",
            "ESC - пауза",
            "",
            "ЦЕЛЬ ИГРЫ:",
            "Уничтожайте волны врагов",
            "Не допускайте столкновения врагов с кораблём",
            "Собирайте улучшения оружия и бонусы",
            "Продержитесь до финальной волны и победите босса",
            "",
            "ОПАСНОСТИ:",
            "- scout: быстрые базовые враги",
            "- zigzag_scout: двигаются зигзагом",
            "- shooter_drone: ведут огонь по игроку",
            "- heavy_fighter: медленные, но живучие",
            "- kamikaze: пикируют в сторону игрока",
            "- sniper: стреляют прицельно",
            "- mine_layer: сбрасывают мины",
            "- teleporter: заходят с флангов",
            "- shielded: сначала нужно пробить щит",
            "- mini_boss: много здоровья и плотный огонь",
            "",
            "СОВЕТЫ:",
            "Не стойте у стены слишком долго",
            "Следите за флангами и падающими минами",
            "Используйте щиты как временное укрытие",
            "Подбирайте улучшения оружия, чтобы быстрее зачищать волны",
            "",
            "ESC - назад в меню",
        ]

        self.scroll_y = 0
        self.max_scroll = 0

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_finished = True
                self.next_scene_name = "menu"
            elif event.key == pygame.K_UP:
                self.scroll_y = min(self.scroll_y + 30, 0)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = max(self.scroll_y - 30, -self.max_scroll)

        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * 30
            self.scroll_y = min(self.scroll_y, 0)
            self.scroll_y = max(self.scroll_y, -self.max_scroll)

    def render(self, screen) -> None:
        screen.fill((15, 15, 25))

        title = self.title_font.render("СПРАВКА", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(self.game.width // 2, 60)))

        start_y = 120 + self.scroll_y
        line_height = 30

        content_height = len(self.lines) * line_height
        visible_height = self.game.height - 150
        self.max_scroll = max(0, content_height - visible_height)

        for i, line in enumerate(self.lines):
            color = (230, 230, 230)
            if line.endswith(":"):
                color = (255, 255, 120)
            elif line.startswith("ESC -"):
                color = (180, 180, 180)

            text = self.font.render(line, True, color)
            screen.blit(text, (40, start_y + i * line_height))

        if self.max_scroll > 0:
            hint = self.small_font.render("UP / DOWN или колесо мыши - прокрутка", True, (160, 160, 160))
            screen.blit(hint, (40, self.game.height - 30))