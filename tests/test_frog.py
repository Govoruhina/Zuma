import unittest
from unittest.mock import patch

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None
from zuma import Frog
from zuma import FlyingBall
from zuma import settings


@unittest.skipIf(pygame is None, 'pygame not installed')
class TestFlyingBall(unittest.TestCase):

    def test_flying_ball_moves(self):
        fb = FlyingBall(
            100, 100,
            1.0, 0.0,
            color=(10, 20, 30),
            speed=100.0,
            radius=5
        )

        x0, y0 = fb.pos[0], fb.pos[1]

        fb.update(0.1)

        self.assertGreater(fb.pos[0], x0)


@unittest.skipIf(pygame is None, 'pygame not installed')
class TestFrogShoot(unittest.TestCase):

    @patch("pygame.time.get_ticks", return_value=100000)
    def test_frog_shoot_changes_colors_and_creates_ball(self, mock_ticks):
        frog = Frog()
        frog._last_shot_time = 0.0

        # детерминированные цвета
        frog.current_ball_color = (11, 22, 33)
        frog.next_ball_color = (44, 55, 66)

        # стреляем в центр
        res = frog.shoot(aim_pos=(0, 0))

        # может вернуть один шар или список
        if isinstance(res, list):
            fb = res[0]
        else:
            fb = res

        self.assertIsInstance(fb, FlyingBall)
        self.assertEqual(fb.color, (11, 22, 33))

        # после выстрела текущий цвет должен смениться
        self.assertEqual(frog.current_ball_color, (44, 55, 66))


if __name__ == "__main__":
    unittest.main()
