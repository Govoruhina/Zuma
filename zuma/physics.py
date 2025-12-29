"""Физика/столкновения.
Функции этого модуля определяют попадание летящего шарика в шар цепочки"""
from __future__ import annotations

from typing import Optional, Sequence


def hit_index(projectile, chain: Sequence) -> Optional[int]:
    # проверяет пересечение окружностей
    try:
        px, py = float(projectile.pos[0]), float(projectile.pos[1])
    except Exception:
        return None

    pr = float(getattr(projectile, "radius", 0.0))
    rr = pr * pr

    for i, b in enumerate(chain):
        bx, by = float(b.pos[0]), float(b.pos[1])
        br = float(getattr(b, "radius", 0.0))
        r = pr + br
        if (px - bx) ** 2 + (py - by) ** 2 <= r * r:
            return i
    return None


def check_collision(flying_ball, chain):
    # Возвращает индекс первого шара, в который попал flying_ball, либо None
    return hit_index(flying_ball, chain)
