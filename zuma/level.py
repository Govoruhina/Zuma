"""Логика уровня: 
параметры и генерация стартовой цепочки шаров"""

from __future__ import annotations

import random
from typing import Dict, List

from . import config as cfg
from . import spiral as path_spiral
from .entities import Ball


def _bonus_type(r: float, *, skull_chance: float) -> str:
    # Пороги вероятностей бонусов
    if r < 0.03:
        return cfg.PowerUp.TYPE_SLOW
    if r < 0.05:
        return cfg.PowerUp.TYPE_REVERSE
    if r < 0.07:
        return cfg.PowerUp.TYPE_FAST_SHOOT
    if r < 0.09:
        return cfg.PowerUp.TYPE_EXPLOSION
    if r < 0.20:
        return cfg.PowerUp.TYPE_BURST_SHOOT
    if r < 0.20 + float(skull_chance):
        return Ball.TYPE_SKULL
    return Ball.TYPE_NORMAL


def _ball_color(kind: str, palette) -> tuple:
    if kind == Ball.TYPE_SKULL:
        return cfg.SKULL_COLOR
    if kind == cfg.PowerUp.TYPE_SLOW:
        return (80, 200, 255)
    if kind == cfg.PowerUp.TYPE_REVERSE:
        return (255, 100, 255)
    if kind == cfg.PowerUp.TYPE_FAST_SHOOT:
        return (255, 200, 0)
    if kind == cfg.PowerUp.TYPE_EXPLOSION:
        return (255, 70, 70)
    if kind == cfg.PowerUp.TYPE_BURST_SHOOT:
        return (30, 60, 70)
    return random.choice(palette)


class Level:
    def __init__(self, number: int):
        self.level_number = int(number)
        self.config: Dict = cfg.LEVELS.get(self.level_number, cfg.LEVELS[1])

        self.base_spiral_speed: float = float(
            self.config.get("spiral_speed", cfg.SPIRAL_SPEED)
            )
        self.spiral_speed: float = float(self.base_spiral_speed)

        self.time_remaining: float = float(self.config.get("time", 60))
        self.target_score: int = int(self.config.get("target_score", 0))

        self.skull_chance: float = float(
            self.config.get("skull_chance", cfg.SKULL_SPAWN_CHANCE)
            )
        self.colors_count: int = int(
            self.config.get("colors_count", len(cfg.BALL_COLORS))
            )

        self.chain: List[Ball] = []
        self.active_powerups: List[dict] = []

        self._spawn_initial_chain()

    def _spawn_initial_chain(self) -> None:
        self.chain.clear()

        n = int(self.config.get("initial_balls", 30))
        spacing = cfg.BALL_DIAMETER + cfg.BALL_SPACING
        t_values = path_spiral.seed_positions(n, spacing=spacing)

        palette = cfg.BALL_COLORS[: max(1, self.colors_count)]
        for t in t_values:
            kind = _bonus_type(random.random(), skull_chance=self.skull_chance)
            col = _ball_color(kind, palette)
            self.chain.append(Ball(color=col, t=float(t), ball_type=kind))

    def activate_powerup(self, powerup_type: str) -> None:
        # добавляет активный бонус в список с таймером
        self.active_powerups.append(
            {"type": str(powerup_type), "remaining": float(cfg.POWERUP_DURATION)}
            )

    def _tick_powerups(self, dt: float) -> None:
        # уменьшает таймеры активных бонусов
        dt = float(dt)
        for p in list(self.active_powerups):
            p["remaining"] -= dt
            if p["remaining"] <= 0:
                self.active_powerups.remove(p)

    def _speed_factor(self) -> float:
        # вычисляет множитель скорости спирали с учётом активных бонусов
        slow = 1.0
        direction = 1.0
        for p in self.active_powerups:
            if p.get("type") == cfg.PowerUp.TYPE_SLOW:
                slow = min(slow, float(cfg.POWERUP_SLOW_FACTOR))
            elif p.get("type") == cfg.PowerUp.TYPE_REVERSE:
                direction = -1.0
        return slow * direction

    def update(self, dt: float) -> None:
        dt = float(dt)
        self._tick_powerups(dt)

        speed = float(self.spiral_speed) * self._speed_factor()
        for b in self.chain:
            b.update(dt, speed=speed)

        self.time_remaining = max(0.0, float(self.time_remaining) - dt)

    def is_complete(self, score: int) -> bool:
        s = int(score)
        return (s >= self.target_score) or (self.time_remaining <= 0.0)

    def spawn_skull(self) -> None:
        if random.random() < float(self.skull_chance):
            self.chain.insert(
                0, Ball(color=cfg.SKULL_COLOR,
                        t=0.0, ball_type=Ball.TYPE_SKULL)
                        )

__all__ = ['Level']
