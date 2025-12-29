"""Точка входа игры.

Файл намеренно остаётся лёгким: инициализируем pygame, 
создаём объект игры и запускаем главный цикл."""
from __future__ import annotations

import sys

try:
    import pygame  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("pygame is required to run the GUI version") from e

from zuma import config as cfg
from zuma.game import Game


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Marble Run — Spiral Shooter")
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    clock = pygame.time.Clock()

    session = Game(screen)
    session.state = "menu"

    running = True
    while running:
        dt = clock.tick(cfg.FPS) / 1000.0
        events = pygame.event.get()

        for ev in events:
            if ev.type == pygame.QUIT:
                running = False

        session.handle_events(events)
        session.update(float(dt))
        session.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
