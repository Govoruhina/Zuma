"""Игровая сессия (контроллер игры).

Отвечает за:
- машину состояний (меню/игра/пауза/экран завершения),
- обработку ввода,
- обновление,
- начисление очков,
- применение бонусов"""
from __future__ import annotations

import sys
from typing import List, Optional, Callable

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from . import config as cfg
from .entities import Ball
from .entities import Frog
from .level import Level
from .chain import group_at, drop_indices, reflow
from .physics import hit_index


def _get(ns, name: str, default):
    return getattr(ns, name, default)


class Game:
    """Одна игровая сессия"""

    def __init__(self, screen=None, *, collide: Callable | None = None):
        self.screen = screen

        self.state: str = "menu"
        self.level_number: int = 1
        self.max_levels: int = int(cfg.MAX_LEVEL)

        self.level: Optional[Level] = None
        self.frog: Frog = Frog()

        self.score: int = 0
        self.lives: int = int(cfg.LIVES)
        self.flying_balls: List[object] = []

        if collide is None:
            collide = check_collision
        self._collide = collide

        # --- чит-коды (ввод с клавиатуры) ---
        self._cheat_code: str = "ZUMA500"
        self._cheat_buffer: str = ""
        self._cheat_buffer_limit: int = 32

    def start_level(self, level_number: int | None = None) -> None:
        # создаёт Level, сбрасывает снаряды, ставит "playing"
        if level_number is not None:
            self.level_number = int(level_number)

        if self.level_number > self.max_levels:
            self.state = "victory"
            return

        self.level = Level(self.level_number)
        self.frog = Frog()
        # Счёт и жизни считаем на уровне: так проще понимать правила и защищать проект.
        self.score = 0
        self.lives = int(cfg.LIVES)
        self.flying_balls.clear()
        self.state = "playing"

    def toggle_pause(self) -> None:
        if self.state == "playing":
            self.state = "paused"
        elif self.state == "paused":
            self.state = "playing"

    # --------------------------- input ---------------------------
    def handle_events(self, events) -> None:  # pragma: no cover
        if pygame is None:
            return

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if (event.type == pygame.MOUSEMOTION 
                and self.state in ("playing", "paused")
                ):
                self.frog.aim_at(event.pos)

            if (event.type == pygame.MOUSEBUTTONDOWN
                 and event.button == 1
                   and self.state == "playing"):
                shots = self.frog.shoot(aim_pos=pygame.mouse.get_pos())
                if shots:
                    self.flying_balls.extend(shots)

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                if self.state in ("playing", "paused"):
                    self.toggle_pause()
                elif self.state == "victory":
                    sys.exit(0)

            if event.key == pygame.K_RETURN:
                if self.state == "menu":
                    self.start_level(1)
                elif self.state == "level_complete":
                    self.level_number += 1
                    self.start_level(self.level_number)
                elif self.state in ("game_over", "victory"):
                    self.level_number = 1
                    self.start_level(1)

            if self.state == "playing":
                if event.key == pygame.K_LEFT:
                    self.frog.rotate(-1)
                elif event.key == pygame.K_RIGHT:
                    self.frog.rotate(1)
                elif event.key == pygame.K_SPACE:
                    shots = self.frog.shoot()
                    if shots:
                        self.flying_balls.extend(shots)
                elif event.key == pygame.K_p:
                    self.toggle_pause()

            # --- чит-коды: ZUMA500  +500 очков ---
            if self.state in ("playing", "paused"):
                if event.key == pygame.K_BACKSPACE:
                    self._cheat_buffer = self._cheat_buffer[:-1]
                else:
                    ch = getattr(event, "unicode", "")
                    if ch and ch.isprintable():
                        self._cheat_buffer += ch.upper()
                        # ограничиваем длину буфера
                        if len(self._cheat_buffer) > self._cheat_buffer_limit:
                            self._cheat_buffer = self._cheat_buffer[-self._cheat_buffer_limit:]

                        if self._cheat_buffer.endswith(self._cheat_code):
                            self.score += 500
                            self._cheat_buffer = ""  # чтобы не срабатывало повторно сразу

    # --------------------------- обновление ---------------------------
    def update(self, dt: float) -> None:
        if self.state != "playing" or self.level is None:
            return

        dt = float(dt)
        self.level.update(dt)
        self.frog.update(dt)

        # бонус: очередь таймер
        if (hasattr(self.frog, "burst_timer")
             and getattr(self.frog, "burst_timer") > 0):
            self.frog.burst_timer -= dt
            if self.frog.burst_timer <= 0:
                self.frog.burst_shoot_count = 1

        collide = self._collide

        for proj in list(self.flying_balls):
            if hasattr(proj, "update"):
                proj.update(dt)
            else:
                try:
                    proj.pos[0] += proj.dx * proj.speed * dt
                    proj.pos[1] += proj.dy * proj.speed * dt
                except Exception:
                    pass

            hit = None
            if collide is not None and self.level.chain:
                hit = collide(proj, self.level.chain)

            if hit is None:
                if hasattr(proj, "is_offscreen") and proj.is_offscreen():
                    self._discard_projectile(proj)
                continue

            self._on_hit(proj, int(hit))
            self._discard_projectile(proj)

            if self.state != "playing":
                return

        self._check_end()

        if self.level.is_complete(self.score):
            self.state = (
                "level_complete" 
                if self.score >= self.level.target_score 
                else "game_over"
                )

    def _discard_projectile(self, proj: object) -> None:
        try:
            self.flying_balls.remove(proj)
        except ValueError:
            pass

    def _on_hit(self, proj: object, idx: int) -> None:
        # обработка попадания снаряда в шар цепочки
        target = self.level.chain[idx]

        if getattr(target, "type", Ball.TYPE_NORMAL) == Ball.TYPE_SKULL:
            # Череп "съедает" жизнь, но не заканчивает уровень сразу.
            # Проигрыш уровня — только если цепочка доехала до конца спирали.
            try:
                self.level.chain.pop(idx)
            except Exception:
                return

            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
                return

            # Сжимаем цепочку, чтобы не осталось дырки после удаления.
            if self.level.chain:
                spacing = cfg.BALL_DIAMETER + cfg.BALL_SPACING
                t0 = float(self.level.chain[0].t)
                reflow(self.level.chain, spacing_px=spacing, t0=t0)
            return

        kind = getattr(target, "type", Ball.TYPE_NORMAL)

        if kind in {
            cfg.PowerUp.TYPE_SLOW,
            cfg.PowerUp.TYPE_REVERSE,
            cfg.PowerUp.TYPE_FAST_SHOOT,
            cfg.PowerUp.TYPE_BURST_SHOOT,
            cfg.PowerUp.TYPE_EXPLOSION,
        }:
            self._pickup_powerup(kind, idx)
            return

        neighbor_t = float(getattr(target, "t", 0.0))
        new_ball = Ball(
            color=getattr(proj, "color", cfg.WHITE), t=neighbor_t + 0.01,
              ball_type=Ball.TYPE_NORMAL
              )
        self.level.chain.insert(idx, new_ball)

        spacing = cfg.BALL_DIAMETER + cfg.BALL_SPACING
        t0 = float(self.level.chain[0].t)
        reflow(self.level.chain, spacing_px=spacing, t0=t0)

        group = group_at(self.level.chain, idx)
        if group:
            removed = drop_indices(self.level.chain, group)
            self.score += int(removed) * int(cfg.POINTS_PER_BALL)

    def _pickup_powerup(self, powerup_type: str, idx: int) -> None:
        # забирает бонус, активирует его эффект
        try:
            self.level.chain.pop(idx)
        except Exception:
            return

        self.score += 150
        self.level.activate_powerup(powerup_type)

        if powerup_type == cfg.PowerUp.TYPE_FAST_SHOOT:
            self.frog.shoot_speed_multiplier = 1.5
        elif powerup_type == cfg.PowerUp.TYPE_BURST_SHOOT:
            self.frog.burst_shoot_count = 3
            self.frog.burst_timer = float(cfg.POWERUP_DURATION)
        elif powerup_type == cfg.PowerUp.TYPE_EXPLOSION:
            radius = 3
            lo = max(0, idx - radius)
            hi = min(len(self.level.chain) - 1, idx + radius)
            if lo <= hi:
                drop_indices(self.level.chain, list(range(lo, hi + 1)))

    def _check_end(self) -> None:
        # Проигрыш уровня, если хвост цепочки доехал до конца спирали.
        # Жизни здесь не расходуются: это именно "поражение уровня".
        if not self.level.chain:
            return

        tail = self.level.chain[-1]
        if hasattr(tail, "is_at_end") and tail.is_at_end():
            self.state = "game_over"
            return

    # --------------------------- отрисовка ---------------------------
    def draw(self, screen) -> None:  # pragma: no cover
        if pygame is None:
            return

        from .ui import (draw_game_over, draw_hud, draw_level_complete,
                          draw_menu, draw_pause_menu, draw_victory)

        screen.fill(cfg.BLACK)

        if self.state == "menu":
            draw_menu(screen)
            return

        if self.state in ("playing", "paused"):
            if self.level:
                for b in self.level.chain:
                    b.draw(screen)
            for p in self.flying_balls:
                if hasattr(p, "draw"):
                    p.draw(screen)
            self.frog.draw(screen)

            next_color = getattr(
                self.frog, "next_ball_color", 
                getattr(self.frog, "current_ball_color", cfg.WHITE)
                )
            current_color = getattr(
                self.frog, "current_ball_color", next_color
                )
            draw_hud(
                screen, self.score, getattr(self.level, "time_remaining", 0),
                  self.level_number, next_color, current_color, lives=self.lives
                  )

            if self.state == "paused":
                draw_pause_menu(screen)
            return

        if self.state == "level_complete":
            draw_level_complete(
                screen, self.score, getattr(self.level, "target_score", 0)
                )
        elif self.state == "game_over":
            draw_game_over(screen, self.score)
        elif self.state == "victory":
            draw_victory(screen, self.score)


check_collision = hit_index

__all__ = ['Game','check_collision']
