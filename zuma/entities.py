"""Сущности игры.

Ball — шар в цепочке, FlyingBall — снаряд, Frog — пушка"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Iterable, Union

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from . import config as cfg
from . import spiral as path_spiral

Point = Tuple[float, float]


@dataclass
class Ball:
    color: Tuple[int, int, int]
    t: float
    kind: str = "normal"

    # константс фор компатибилитй
    TYPE_NORMAL = "normal"
    TYPE_SKULL = "skull"

    def __init__(
            self, color: Tuple[int, int, int], t: float,
            ball_type: str = "normal", kind: str | None = None
            ):
        if kind is None:
            kind = ball_type
        self.color = tuple(color)
        self.t = float(t)
        self.kind = str(kind)
        self.__post_init__()


    def __post_init__(self):
        self.t = float(self.t)
        self.type = self.kind
        self.radius: int = int(cfg.BALL_RADIUS)
        self.pos: Point = self._xy(self.t)

    def _xy(self, t: float) -> Point:
        x, y = path_spiral.xy(float(t))
        return (float(x), float(y))

    def calculate_position(self) -> Point:
        return self._xy(self.t)

    def update(self, dt: float, speed: float | None = None) -> None:
        v = cfg.SPIRAL_SPEED if speed is None else float(speed)
        self.t += float(dt) * v
        self.pos = self._xy(self.t)

    def draw(self, screen) -> None:  # pragma: no cover
        if pygame is None:
            return
        x, y = int(self.pos[0]), int(self.pos[1])

        is_skull = self.type == self.TYPE_SKULL
        fill = cfg.SKULL_COLOR if is_skull else self.color
        outline = cfg.WHITE if is_skull else (20, 20, 26)

        pygame.draw.circle(screen, fill, (x, y), self.radius)
        pygame.draw.circle(screen, outline, (x, y), self.radius, 2)

        if is_skull:
        # Характерный вид «черепа», а не просто крестик (X)
            pygame.draw.circle(screen, (15, 15, 18), (x - 5, y - 3), 3)
            pygame.draw.circle(screen, (15, 15, 18), (x + 5, y - 3), 3)
            pygame.draw.line(
                screen, (15, 15, 18), (x - 4, y + 6),
                  (x + 4, y + 6), 2
                  )

        # Для бонусных шаров рисуем маленькую букву, чтобы различать их
        if not is_skull and self.type in {
            cfg.PowerUp.TYPE_SLOW,
            cfg.PowerUp.TYPE_REVERSE,
            cfg.PowerUp.TYPE_FAST_SHOOT,
            cfg.PowerUp.TYPE_EXPLOSION,
            cfg.PowerUp.TYPE_BURST_SHOOT,
        }:
            glyph = {
                cfg.PowerUp.TYPE_SLOW: "S",
                cfg.PowerUp.TYPE_REVERSE: "R",
                cfg.PowerUp.TYPE_FAST_SHOOT: "F",
                cfg.PowerUp.TYPE_EXPLOSION: "X",
                cfg.PowerUp.TYPE_BURST_SHOOT: "B",
            }.get(self.type, "?")
            try:
                font = pygame.font.SysFont(None, 18, bold=True)
                img = font.render(glyph, True, (245, 245, 250))
                sh = font.render(glyph, True, (10, 10, 12))
                r = img.get_rect(center=(x, y - 1))
                screen.blit(sh, (r.x + 1, r.y + 1))
                screen.blit(img, r)
            except Exception:
                pass

    def distance_to(
            self, other: Union["Ball", Point, Iterable[float]]
            ) -> float:
        if isinstance(other, Ball):
            ox, oy = other.pos
        else:
            other = list(other)
            ox, oy = float(other[0]), float(other[1])
        dx = float(self.pos[0]) - float(ox)
        dy = float(self.pos[1]) - float(oy)
        return (dx * dx + dy * dy) ** 0.5

    def is_at_end(self) -> bool:
        r = cfg.SPIRAL_START_RADIUS - self.t * cfg.SPIRAL_TIGHTNESS
        return r <= cfg.SPIRAL_END_RADIUS


Ball = Ball

import math
from dataclasses import dataclass
from typing import List, Tuple

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from . import config as cfg


@dataclass
class FlyingBall:
    pos: List[float]
    vx: float
    vy: float
    color: Tuple[int, int, int]
    speed: float
    radius: float
    kind: str = "normal"

    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        color: Tuple[int, int, int],
        *,
        speed: float | None = None,
        radius: float | None = None,
        ball_type: str = "normal",
    ) -> None:
        self.pos = [float(x), float(y)]

        mag = math.hypot(dx, dy)
        if mag <= 1e-9:
            nx, ny = 1.0, 0.0
        else:
            nx, ny = float(dx) / mag, float(dy) / mag

        self.vx, self.vy = nx, ny
        self.speed = float(cfg.SHOT_SPEED if speed is None else speed)
        self.radius = float(cfg.BALL_RADIUS if radius is None else radius)
        self.color = color
        self.type = str(ball_type)
        self.kind = self.type

    def update(self, dt: float) -> None:
        self.pos[0] += self.vx * self.speed * float(dt)
        self.pos[1] += self.vy * self.speed * float(dt)

    def draw(self, screen) -> None:  # pragma: no cover
        if pygame is None:
            return
        x, y = int(self.pos[0]), int(self.pos[1])
        pygame.draw.circle(screen, self.color, (x, y), int(self.radius))
        pygame.draw.circle(screen, (15, 15, 18), (x, y), int(self.radius), 1)

    def is_offscreen(self) -> bool:
        x, y = self.pos
        r = float(self.radius)
        return x < -r or x > cfg.WIDTH + r or y < -r or y > cfg.HEIGHT + r


FlyingBall = FlyingBall

import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Tuple

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from . import config as cfg


Point = Tuple[float, float]


def _clock_seconds() -> float:
    if pygame is not None:
        try:
            return pygame.time.get_ticks() / 1000.0
        except Exception:
            pass
    return time.monotonic()


@dataclass
class Frog:
    pos: Point = field(
        default_factory=lambda:
        (float(cfg.FROG_X),float(cfg.FROG_Y))
        )
    angle: float = 0.0
    _aim: float = 0.0

    # задержка между выстрелами
    cooldown_base: float = 0.8
    cooldown_multiplier: float = 1.0
    _last_shot_time: float = 0.0

    radius: int = int(cfg.FROG_RADIUS)

    current_ball_color: Tuple[int, int, int] = field(
        default_factory=lambda: random.choice(cfg.BALL_COLORS)
        )
    next_ball_color: Tuple[int, int, int] = field(
        default_factory=lambda: random.choice(cfg.BALL_COLORS)
        )

    shoot_speed_multiplier: float = 1.0
    burst_shoot_count: int = 1
    burst_angle_spread: float = math.radians(10)

    shot_cooldown: float = 0.0
    shot_cooldown_time: float = 0.2

    def rotate(self, direction: int) -> None:
        self._aim += math.radians(cfg.FROG_ROTATION_SPEED) * int(direction)

    def aim_at(self, target_pos: Point) -> None:
        dx = float(target_pos[0]) - float(self.pos[0])
        dy = float(target_pos[1]) - float(self.pos[1])
        self._aim = math.atan2(dy, dx)

    def update(self, dt: float) -> None:
        dt = float(dt)
        if self.shot_cooldown > 0.0:
            self.shot_cooldown = max(0.0, self.shot_cooldown - dt)

        # Плавный поворот к цели
        delta = (self._aim - self.angle + math.pi) % (2 * math.pi) - math.pi
        cap = math.radians(cfg.FROG_ROTATION_SPEED) * dt * 5.0
        if abs(delta) > cap:
            self.angle += cap if delta > 0 else -cap
        else:
            self.angle = self._aim

    def can_shoot(self, now_time: float | None = None) -> bool:
        # Проверяет, можно ли выстрелить
        now = _clock_seconds() if now_time is None else float(now_time)
        cd = self.cooldown_base * self.cooldown_multiplier
        return (now - float(self._last_shot_time)) >= float(cd)

    def _projectile(self, ang: float) -> FlyingBall:
        x, y = self.pos
        dx, dy = math.cos(ang), math.sin(ang)
        return FlyingBall(
            x=x,
            y=y,
            dx=dx,
            dy=dy,
            color=self.current_ball_color,
            speed=cfg.SHOT_SPEED * float(self.shoot_speed_multiplier),
            radius=cfg.BALL_RADIUS,
            ball_type="normal",
        )

    def shoot(self, aim_pos: Point | None = None) -> List[FlyingBall]:
        # Выполняет выстрел, возвращает список снарядов
        if not self.can_shoot():
            return []

        if aim_pos is not None:
            self.aim_at(aim_pos)

        n = max(1, int(getattr(self, "burst_shoot_count", 1)))
        if n == 1:
            angles = [self.angle]
        else:
            spread = float(getattr(self, "burst_angle_spread", math.radians(10)))
            mid = (n - 1) / 2.0
            angles = [self.angle + (i - mid) * (spread / max(1.0, mid)) for i in range(n)]

        shots = [self._projectile(a) for a in angles]

        # Прокрутить боезапас (текущий шар → следующий)
        self.current_ball_color = self.next_ball_color
        self.next_ball_color = random.choice(cfg.BALL_COLORS)

        self._last_shot_time = _clock_seconds()
        self.shot_cooldown = self.shot_cooldown_time
        return shots

    def draw(self, screen) -> None:  # pragma: no cover
        if pygame is None:
            return

        x, y = int(self.pos[0]), int(self.pos[1])
        pygame.draw.circle(screen, (70, 200, 120), (x, y), self.radius)
        pygame.draw.circle(screen, (15, 15, 18), (x, y), self.radius, 2)

        # Индикатор боезапаса (текущий + следующий) рисуем рядом с пушкой
        r = int(max(6, cfg.BALL_RADIUS))
        cur_pos = (x, y - self.radius - r - 6)
        nxt_pos = (x + self.radius + r + 10, y - self.radius - r - 6)

        pygame.draw.circle(screen, self.current_ball_color, cur_pos, r)
        pygame.draw.circle(screen, (15, 15, 18), cur_pos, r, 2)

        pygame.draw.circle(screen, self.next_ball_color, nxt_pos, r)
        pygame.draw.circle(screen, (15, 15, 18), nxt_pos, r, 2)

        # прицел
        length = self.radius * 2
        ex = x + length * math.cos(self.angle)
        ey = y + length * math.sin(self.angle)
        pygame.draw.line(screen, (240, 240, 245), (x, y), (ex, ey), 3)

__all__ = ['Ball','FlyingBall','Frog']
