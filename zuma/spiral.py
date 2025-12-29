"""Утилиты спиральной траектории.

Игра хранит положение шаров как параметр t.
Этот модуль переводит t в координаты (x, y), 
оценивает расстояния вдоль спирали и помогает подбирать
шаг t под заданную дистанцию."""
from __future__ import annotations

import math
from typing import Tuple, List

from . import config as cfg


def radius_for(t: float) -> float:
    return max(0.0, cfg.SPIRAL_START_RADIUS - cfg.SPIRAL_TIGHTNESS * t)


def angle_for(t: float) -> float:
    return 0.2 * t


def xy(t: float) -> Tuple[float, float]:
    r = radius_for(t)
    a = angle_for(t)
    return (
        cfg.SPIRAL_CENTER_X + r * math.cos(a),
        cfg.SPIRAL_CENTER_Y + r * math.sin(a)
        )


def chord_length(t0: float, t1: float) -> float:
    # Вычисляет расстояние по прямой между двумя точками спирали
    x0, y0 = xy(t0)
    x1, y1 = xy(t1)
    return math.hypot(x1 - x0, y1 - y0)


def step_t(
        start_t: float, target_dist: float, *,
        forward: bool = True, tol: float = 0.5, cap: int = 200
        ) -> float:
    # Подбирает новое t, чтобы расстояние от start_t было близко к target_dist
    sign = 1.0 if forward else -1.0
    probe = start_t
    step = sign * 1.0

    for _ in range(cap):
        nxt = probe + step
        d = chord_length(start_t, nxt)
        err = d - target_dist
        if abs(err) <= tol:
            return nxt

      # Если недобрали расстояние — продолжаем идти в том же направлении
        if err < 0:
            probe = nxt
            continue

        # Если пересекли расстояние — сокращаем шаг
        step *= 0.5

    return probe + step


def seed_positions(count: int, spacing: float | None = None) -> List[float]:
    # Генерирует стартовые значения t для цепочки с равным расстоянием между шариками
    if count <= 0:
        return []
    if spacing is None:
        spacing = cfg.BALL_DIAMETER + cfg.BALL_SPACING

    t = 0.0
    res = [t]
    for _ in range(count - 1):
        t = step_t(t, spacing, forward=True)
        res.append(t)
    return res


# ---------------------------------------------------------------------------
# Удобные обёртки
# ---------------------------------------------------------------------------

def get_radius(t):
    return radius_for(float(t))

def get_position(t):
    return xy(float(t))

def distance_between_t(t1, t2):
    return chord_length(float(t1), float(t2))

def find_t_at_distance(start_t, distance, forward=True, tol=0.5, max_iter=200):
    return step_t(
        float(start_t), float(distance), forward=bool(forward), tol=float(tol),
        cap=int(max_iter)
        )

def get_initial_ball_positions(num_balls, spacing=None):
    return seed_positions(int(num_balls), spacing)
