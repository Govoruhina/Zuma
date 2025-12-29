"""Отрисовка интерфейса (UI).
HUD, меню, оверлеи (пауза/победа/поражение) и подсказка бонусов"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

try:
    import pygame  # type: ignore
except Exception:  # pragma: no cover
    pygame = None  # type: ignore

from . import config as cfg


Color = Tuple[int, int, int]


@dataclass(frozen=True)
class HudState:
    score: int
    level: int
    seconds_left: float
    current_color: Color
    next_color: Color
    # Количество жизней (используем для подсказок и отображения в HUD).
    lives: int = 0

def _font(size: int):
    if pygame is None:
        return None
    return pygame.font.Font(None, size)


def _shadow_text(
        surface, text: str, pos: Tuple[int, int], size: int, 
        color: Color, shadow: Color = (0, 0, 0)
        ):
    if pygame is None:
        return
    f = _font(size)
    if not f:
        return
    img = f.render(text, True, color)
    sh = f.render(text, True, shadow)
    surface.blit(sh, (pos[0] + 2, pos[1] + 2))
    surface.blit(img, pos)

def _format_time(seconds_left: float) -> str:
    """Формат времени в виде ММ:СС."""
    total = int(max(0.0, seconds_left))
    mm = total // 60
    ss = total % 60
    return f"{mm:02d}:{ss:02d}"


def _draw_heart(surface, x: int, y: int, size: int, color: Color):
    """Рисует простое сердечко примитивами pygame.
    (x, y) — левый верхний угол области сердечка."""
    if pygame is None:
        return
    # Две "доли" сердца
    r = size // 4
    cx1 = x + r
    cx2 = x + 3 * r
    cy = y + r
    pygame.draw.circle(surface, color, (cx1, cy), r)
    pygame.draw.circle(surface, color, (cx2, cy), r)
    # Нижняя часть — треугольник
    pts = [(x, y + r), (x + size, y + r), (x + size // 2, y + size)]
    pygame.draw.polygon(surface, color, pts)


def _legend_dot(
        surface, center: Tuple[int, int], color: Color,
        radius: int = 8, border: Color = (20, 20, 24)
        ):
    # бонусы
    if pygame is None:
        return
    pygame.draw.circle(surface, border, center, radius + 2)
    pygame.draw.circle(surface, color, center, radius)


def _legend_item(
        surface, label: str, color: Color, x: int, y: int,
        glyph: Optional[str] = None
        ):
    """Одна строка в легенде бонусов."""
    if pygame is None:
        return
    _legend_dot(surface, (x + 10, y + 10), color, radius=7)
    if glyph:
        _shadow_text(surface, glyph, (x + 6, y + 2), 14, (245, 245, 250))
    _shadow_text(surface, label, (x + 26, y + 2), 16, (210, 210, 225))



def _round_rect(
        surface, rect, fill_rgba, radius: int = 14,
        border: Optional[Color] = None, border_w: int = 2
        ):
    # Рисует прямоугольник с закруглёнными углами
    if pygame is None:
        return

    box = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(box, fill_rgba, box.get_rect(), border_radius=radius)
    surface.blit(box, (rect.x, rect.y))

    if border is not None and border_w > 0:
        pygame.draw.rect(surface, border, rect, border_w, border_radius=radius)


def _draw_time_gauge(
        surface, center: Tuple[int, int], radius: int, ratio: float
        ):
    if pygame is None:
        return

    ratio = max(0.0, min(1.0, ratio))
    # базовое кольцо
    pygame.draw.circle(surface, (30, 30, 36), center, radius, 8)

    # дуга прогресса
    end_angle = -3.14159 / 2 + ratio * 2 * 3.14159
    steps = max(12, int(120 * ratio) + 12)
    pts = []
    for i in range(steps + 1):
        a = -3.14159 / 2 + (end_angle + 3.14159 / 2) * (i / steps)
        x = center[0] + int(radius * 0.92 * __import__("math").cos(a))
        y = center[1] + int(radius * 0.92 * __import__("math").sin(a))
        pts.append((x, y))

    if len(pts) > 1:
        warn = ratio <= (
            cfg.UI_TIMER_WARNING_THRESHOLD 
            / max(1.0, cfg.LEVELS.get(1, {}).get("time", 60))
            )
        col = cfg.UI_TIMER_WARNING_COLOR if warn else (120, 200, 255)
        pygame.draw.lines(surface, col, False, pts, 7)


def _skull_badge(surface, pos: Tuple[int, int]):
    # Мини-значок черепа
    if pygame is None:
        return

    x, y = pos
    # голова
    pygame.draw.circle(surface, (210, 210, 225), (x + 14, y + 14), 13)
    # глаза
    pygame.draw.circle(surface, (20, 20, 26), (x + 9, y + 13), 4)
    pygame.draw.circle(surface, (20, 20, 26), (x + 19, y + 13), 4)
    # челюсть
    jaw = pygame.Rect(x + 7, y + 20, 14, 10)
    pygame.draw.rect(surface, (210, 210, 225), jaw, border_radius=4)
    for i in range(3):
        pygame.draw.line(
            surface, (20, 20, 26), (x + 9 + i * 4, y + 22),
              (x + 9 + i * 4, y + 29), 1
              )


def draw_play_hud(screen, hud: HudState):
    # HUD: левая панель + верхний баннер
    if pygame is None:
        return

    w, h = screen.get_size()

    # Боковая панель
    panel_w = 220
    _round_rect(
        screen,
        pygame.Rect(14, 14, panel_w, h - 28),
        cfg.UI_BACKGROUND_COLOR,
        radius=18,
        border=(60, 60, 72),
        border_w=2,
    )

    _shadow_text(screen, "MARBLE RUN", (30, 26), 30, (235, 235, 245))
    _shadow_text(screen, f"LEVEL {hud.level}", (30, 62), 22, (210, 210, 235))

    # Блок счёта
    _shadow_text(screen, "SCORE", (30, 108), 18, (170, 170, 190))
    _shadow_text(screen, f"{hud.score:06d}", (30, 128), 34, (255, 235, 140))

    # Жизни
    if hud.lives:
        _shadow_text(screen, "ЖИЗНИ", (30, 164), 18, (170, 170, 190))
        # Рисуем сердечки (а не текст), чтобы было видно даже на маленьком шрифте
        hx, hy = 30, 186
        for i in range(int(max(0, hud.lives))):
            _draw_heart(screen, hx + i * 20, hy, 16, (235, 80, 95))

    # Время (цифрами)
    _shadow_text(screen, "TIME", (30, 220), 18, (170, 170, 190))
    time_txt = _format_time(hud.seconds_left)
    _shadow_text(screen, time_txt, (30, 244), 34, (230, 230, 240))
    # Боезапас показываем рядом с лягушкой (текущий + следующий)


    # подсказка бонусов: цвета и буквы совпадают с тем, что рисуется на шарах
    _shadow_text(screen, "БОНУСЫ", (30, 278), 18, (170, 170, 190))
    bx, by = 30, 300
    _legend_item(
        screen, "S  замедление", (80, 200, 255), bx, by + 0, glyph="S"
        )
    _legend_item(
        screen, "R  обратный ход", (255, 100, 255), bx, by + 26, glyph="R"
        )
    _legend_item(
        screen, "F  быстрее вылет", (255, 200, 0), bx, by + 52, glyph="F"
        )
    _legend_item(
        screen, "X  взрыв", (255, 70, 70), bx, by + 78, glyph="X"
        )
    _legend_item(
        screen, "B  очередь", (30, 60, 70), bx, by + 104, glyph="B"
        )

    _shadow_text(screen, "ЦВЕТА ШАРОВ", (30, 440), 18, (170, 170, 190))
    cx, cy = 30, 464
    for n, col in enumerate(cfg.BALL_COLORS[:6]):
        _legend_dot(screen, (cx + 16 + n * 28, cy + 10), col, radius=9)

    _skull_badge(screen, (30, h - 70))
    _shadow_text(screen, "ЧЕРЕП = -1 ЖИЗНЬ", (62, h - 64), 18, (200, 200, 215))

    # Верхний баннер
    banner = pygame.Rect(panel_w + 28, 14, w - (panel_w + 42), 54)
    _round_rect(
        screen, banner, (20, 20, 26, 140), 
        radius=16, border=(50, 50, 62), border_w=2
        )
    _shadow_text(
        screen, "Esc: pause   Space/Click: shoot   P: pause",
          (banner.x + 16, banner.y + 16), 20, (210, 210, 225)
          )


def draw_overlay(
        screen, title: str, subtitle: str = "",
          accent: Color = (255, 235, 140)
          ):
    # затемнение и надпись
    if pygame is None:
        return

    w, h = screen.get_size()
    fade = pygame.Surface((w, h), pygame.SRCALPHA)
    fade.fill((0, 0, 0, 170))
    screen.blit(fade, (0, 0))

    box = pygame.Rect(0, 0, min(560, w - 80), 220)
    box.center = (w // 2, h // 2)

    _round_rect(
        screen, box, (16, 16, 22, 220), radius=26,
          border=(70, 70, 90), border_w=2
          )

    _shadow_text(
        screen, title, (box.x + 28, box.y + 34), 54, accent
        )
    if subtitle:
        _shadow_text(
            screen, subtitle, (box.x + 28, box.y + 120), 26, (230, 230, 240)
            )


def draw_main_menu(screen):
    if pygame is None:
        return

    w, h = screen.get_size()

    # Тёмная подложка
    backdrop = pygame.Surface((w, h))
    backdrop.fill((8, 8, 10))
    screen.blit(backdrop, (0, 0))

    # Карточка заголовка
    card = pygame.Rect(0, 0, min(620, w - 80), 280)
    card.center = (w // 2, h // 2)
    _round_rect(
        screen, card, (18, 18, 26, 230), radius=28, 
        border=(80, 80, 100), border_w=2
        )

    _shadow_text(
        screen, "MARBLE RUN", (card.x + 40, card.y + 46), 72, (255, 235, 140)
        )
    _shadow_text(
        screen, "A spiral shooter with a grumpy frog.",
          (card.x + 42, card.y + 130), 26, (220, 220, 235)
        )
    _shadow_text(
        screen, "Enter  — start", (card.x + 42, card.y + 184),
          24, (200, 200, 220)
        )
    _shadow_text(
        screen, "Esc    — exit", (card.x + 42, card.y + 218),
          24, (200, 200, 220)
        )

def _safe_ratio(seconds_left: float, level: int) -> float:
    # Оценка по возможности: используем настроенное время текущего уровня
    total = float(cfg.LEVELS.get(int(level), {}).get("time", 60))
    if total <= 0:
        return 0.0
    return max(0.0, min(1.0, seconds_left / total))


# ---------------------------------------------------------------------------
# UI‑фасад
# ---------------------------------------------------------------------------

def draw_hud(
        screen, score, time_left, level_number,
        next_ball_color=None, current_ball_color=None, lives: int | None = None
        ):
    """Совместимый фасад: принимает time_left, но в HudState используется seconds_left."""
    # Защита от None: если цветов нет, берём первый базовый цвет.
    cur = current_ball_color or next_ball_color or cfg.BALL_COLORS[0]
    nxt = next_ball_color or current_ball_color or cfg.BALL_COLORS[0]

    state = HudState(
        score=int(score),
        level=int(level_number),
        seconds_left=float(time_left),
        current_color=cur,
        next_color=nxt,
        lives=int(lives) if lives is not None else 0,
    )
    draw_play_hud(screen, state)

def draw_menu(screen):
    draw_main_menu(screen)

def draw_pause_menu(screen):
    draw_overlay(screen, "ПАУЗА", "Esc — продолжить")

def draw_level_complete(screen, score=0, target_score=0):
    subtitle = f"Счёт: {int(score)} / {int(target_score)}. Enter — следующий уровень"
    draw_overlay(screen, "УРОВЕНЬ ПРОЙДЕН", subtitle)

def draw_game_over(screen, score=0):
    subtitle = f"Счёт: {int(score)}. Enter — заново"
    draw_overlay(screen, "ИГРА ОКОНЧЕНА", subtitle)

def draw_victory(screen, score=0):
    subtitle = f"Итоговый счёт: {int(score)}. Enter — сыграть ещё раз"
    draw_overlay(screen, "ПОБЕДА", subtitle)
