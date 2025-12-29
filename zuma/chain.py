"""Операции с цепочкой шаров.

Здесь находятся функции для:
- выравнивания цепочки по расстоянию между шарами,
- продвижения шаров по спирали,
- добавления новых шаров в цепочки,
- поиска одноцветных групп и удаления шаров."""
from __future__ import annotations

import random
from typing import List, Sequence, Optional

from . import config as cfg
from . import spiral as path_spiral

from .entities import Ball


def _gap_t(spacing_px: float) -> float:
    # Переводим расстояние в пикселях в шаг t спирали
    return float(spacing_px) / float(cfg.SPIRAL_TIGHTNESS)


def reflow(
        chain: List[Ball], *, spacing_px: Optional[float] = None,
          t0: Optional[float] = None
          ) -> None:
    # Выравнивает цепочку по заданному расстоянию между шарами
    if not chain:
        return

    spacing_px = float(
        cfg.BALL_DIAMETER + 
        cfg.BALL_SPACING if spacing_px is None else spacing_px
        )
    cur_t = float(chain[0].t if t0 is None else t0)

    chain[0].t = cur_t
    chain[0].pos = (
        chain[0].calculate_position() 
        if hasattr(chain[0], "calculate_position") 
        else path_spiral.xy(cur_t)
        )

    for b in chain[1:]:
        cur_t = path_spiral.step_t(cur_t, spacing_px, forward=True)
        b.t = float(cur_t)
        b.pos = (
            b.calculate_position() 
            if hasattr(b, "calculate_position") 
            else path_spiral.xy(cur_t)
            )


def prepend_wave(
        chain: List[Ball], count: int, *,
        skull_rate: Optional[float] = None, palette: Sequence = ()
        ) -> None:
    # Добавляет новые шары в начало цепочки
    skull_rate = (
        cfg.SKULL_SPAWN_CHANCE 
        if skull_rate is None 
        else float(skull_rate)
        )
    colors = list(palette) if palette else list(cfg.BALL_COLORS)

    # Новые шары вставляются в цепочку — перед самым первым шаром
    step_t = _gap_t(cfg.BALL_DIAMETER + cfg.BALL_SPACING)
    head_t = float(chain[0].t) if chain else 0.0

    for i in range(int(count)):
        t = head_t - (i + 1) * step_t
        is_skull = random.random() < skull_rate
        btype = Ball.TYPE_SKULL if is_skull else Ball.TYPE_NORMAL
        col = cfg.SKULL_COLOR if is_skull else random.choice(colors)
        chain.insert(0, Ball(color=col, t=t, ball_type=btype))


def advance(chain: List[Ball], dt: float, speed: float) -> str | None:
    # двигает шары и проверяет конец цепочки
    for b in chain:
        b.update(float(dt), speed=float(speed))

    end_t = (
        (cfg.SPIRAL_START_RADIUS - cfg.SPIRAL_END_RADIUS)
          / cfg.SPIRAL_TIGHTNESS
          )
    if chain and chain[-1].t >= end_t:
        return "game_over"
    return None


def group_at(chain: List[Ball], index: int) -> List[int]:
    # ищет группу шаров
    if index < 0 or index >= len(chain):
        return []

    wanted = chain[index].color
    lo = index
    hi = index

    while lo - 1 >= 0 and chain[lo - 1].color == wanted:
        lo -= 1
    while hi + 1 < len(chain) and chain[hi + 1].color == wanted:
        hi += 1

    if (hi - lo + 1) < int(cfg.MIN_MATCH):
        return []
    return list(range(lo, hi + 1))


def drop_indices(chain: List[Ball], indices: List[int]) -> int:
    if not indices:
        return 0

    for i in sorted(set(indices), reverse=True):
        if 0 <= i < len(chain):
            del chain[i]
    return len(indices)
