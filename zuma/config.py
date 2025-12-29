"""Конфигурация игры.

В этом модуле собраны константы
(размер окна, параметры спирали, цвета, очки, жизни),
а также параметры уровней и вероятности появления
специальных шаров/бонусов.

Здесь же есть небольшие функции для геометрии спирали,
чтобы их было удобно тестировать."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List
import math
import random

Color = Tuple[int, int, int]


class PowerUp:
    TYPE_BURST_SHOOT = "burst_shoot"
    TYPE_SLOW = "slow"
    TYPE_FAST_SHOOT = "fast_shoot"
    TYPE_REVERSE = "reverse"
    TYPE_EXPLOSION = "explosion"


# ---------------------------------------------------------------------------
# Скрин / тайминг
# ---------------------------------------------------------------------------
WIDTH: int = 800
HEIGHT: int = 600
FPS: int = 60


# ---------------------------------------------------------------------------
# цвета
# ---------------------------------------------------------------------------
WHITE: Color = (255, 255, 255)
BLACK: Color = (0, 0, 0)
GRAY: Color = (128, 128, 128)
RED: Color = (255, 0, 0)
GREEN: Color = (0, 255, 0)
BLUE: Color = (0, 0, 255)
YELLOW: Color = (255, 255, 0)
PURPLE: Color = (128, 0, 128)
ORANGE: Color = (255, 165, 0)

BALL_COLORS: List[Color] = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE]
SKULL_COLOR: Color = (45, 45, 55)


# ---------------------------------------------------------------------------
# цепочка
# ---------------------------------------------------------------------------
BALL_RADIUS: int = 15
BALL_DIAMETER: int = BALL_RADIUS * 2
BALL_SPACING: int = 2

MIN_MATCH: int = 3
POINTS_PER_BALL: int = 10


# ---------------------------------------------------------------------------
# Спиральная траектория
# ---------------------------------------------------------------------------
SPIRAL_CENTER_X: int = WIDTH // 2
SPIRAL_CENTER_Y: int = HEIGHT // 2
SPIRAL_START_RADIUS: int = 250
SPIRAL_END_RADIUS: int = 30
SPIRAL_TIGHTNESS: float = 1.5
SPIRAL_SPEED: float = 1.5


def spiral_xy(t: float) -> Tuple[float, float]:
    """Возвращает координаты (x, y) точки спирали для параметра t.

Важно: t — это не угол. Это параметр движения вдоль траектории,
 подобранный под геймплей (плотность витков, скорость и т.п.)."""
    r = SPIRAL_START_RADIUS - t * SPIRAL_TIGHTNESS
    ang = t * 0.2
    return (
        SPIRAL_CENTER_X + r * math.cos(ang),
        SPIRAL_CENTER_Y + r * math.sin(ang),
    )


def get_spiral_position(t: float) -> Tuple[float, float]:
    return spiral_xy(t)


def spiral_x(t: float) -> float:
    return spiral_xy(t)[0]


def spiral_y(t: float) -> float:
    return spiral_xy(t)[1]


def get_initial_ball_positions(count: int) -> List[float]:
    """Генерирует стартовые значения t вдоль используемого участка спирали."""
    if count <= 0:
        return []

    start_t = 0.0
    usable = (SPIRAL_START_RADIUS - SPIRAL_END_RADIUS) / SPIRAL_TIGHTNESS
    end_t = usable * 0.85

    step = end_t / (count + 1)
    values = [start_t + i * step for i in range(1, count + 1)]
    random.shuffle(values)
    return values


# ---------------------------------------------------------------------------
# шутер (лягушка)
# ---------------------------------------------------------------------------
FROG_X: int = WIDTH // 2
FROG_Y: int = HEIGHT // 2
FROG_RADIUS: int = 20
FROG_ROTATION_SPEED: int = 180
SHOT_SPEED: int = 250


# ---------------------------------------------------------------------------
# череп / правила
# ---------------------------------------------------------------------------
SKULL_SPAWN_CHANCE: float = 0.05
SKULL_EFFECT_RADIUS: int = 2

LIVES: int = 3
COLLISION_DISTANCE: int = BALL_RADIUS + 5


# ---------------------------------------------------------------------------
# Power-ups
# ---------------------------------------------------------------------------
POWERUP_DURATION: float = 6.0
POWERUP_SLOW_FACTOR: float = 0.35


# ---------------------------------------------------------------------------
# Уровни
# ---------------------------------------------------------------------------
LEVELS = {
    1: {"time": 60, "target_score": 600, "spiral_speed": 0.6,
         "initial_balls": 50, "skull_chance": 0.03, "colors_count": 4},
    2: {"time": 90, "target_score": 800, "spiral_speed": 1,
         "initial_balls": 60, "skull_chance": 0.05, "colors_count": 5},
    3: {"time": 120, "target_score": 1000, "spiral_speed": 1,
         "initial_balls": 60, "skull_chance": 0.07, "colors_count": 6},
    4: {"time": 150, "target_score": 1500, "spiral_speed": 1,
         "initial_balls": 55, "skull_chance": 0.08, "colors_count": 6},
    5: {"time": 180, "target_score": 2000, "spiral_speed": 1,
         "initial_balls": 40, "skull_chance": 0.1, "colors_count": 6},
}

MAX_LEVEL: int = 5


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
FONT_SIZE: int = 22
FONT_SIZE_LARGE: int = 44
UI_MARGIN: int = 12

UI_TEXT_COLOR: Color = WHITE
UI_BACKGROUND_COLOR = (10, 10, 14, 160)
UI_TIMER_WARNING_COLOR: Color = ORANGE
UI_TIMER_WARNING_THRESHOLD: int = 10
