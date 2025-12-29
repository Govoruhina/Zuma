import unittest

from zuma import Ball
from zuma import spiral, settings


class TestBall(unittest.TestCase):

    def test_calculate_position_matches_spiral(self):
        b = Ball(color=(10, 20, 30), t=0.0, ball_type=Ball.TYPE_NORMAL)
        self.assertEqual(b.pos, spiral.get_position(0.0))
        self.assertEqual(b.radius, settings.BALL_RADIUS)

    def test_update_advances_t_and_pos(self):
        b = Ball(color=(1, 2, 3), t=0.0)
        old_t = b.t

        b.update(0.5, speed=2.0)

        self.assertGreater(b.t, old_t)
        self.assertEqual(b.pos, spiral.get_position(b.t))

    def test_distance_to_point_and_is_at_end(self):
        b = Ball(color=(1, 2, 3), t=0.0)

        self.assertAlmostEqual(b.distance_to(b), 0.0, places=6)

        self.assertIsInstance(b.is_at_end(), bool)


if __name__ == "__main__":
    unittest.main()
