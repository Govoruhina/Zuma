import unittest
from zuma import spiral
from zuma import settings


class TestSpiralGetPosition(unittest.TestCase):
    def test_get_position_returns_tuple(self):
        p = spiral.get_position(0.0)
        self.assertIsInstance(p, tuple)
        self.assertEqual(len(p), 2)


class TestSpiralGetRadius(unittest.TestCase):
    def test_radius_decreases_with_t(self):
        r0 = spiral.get_radius(0.0)
        r1 = spiral.get_radius(10.0)
        self.assertLessEqual(r1, r0)


class TestSpiralDistanceBetweenT(unittest.TestCase):
    def test_distance_between_t_positive(self):
        d = spiral.distance_between_t(0.0, 5.0)
        self.assertGreaterEqual(d, 0.0)


class TestSpiralFindTAtDistance(unittest.TestCase):
    def test_find_t_at_distance_monotonic(self):
        t0 = 0.0
        spacing = settings.BALL_DIAMETER + settings.BALL_SPACING
        t1 = spiral.find_t_at_distance(t0, spacing, forward=True)
        self.assertIsInstance(t1, float)
        self.assertNotEqual(t1, t0)


if __name__ == "__main__":
    unittest.main()