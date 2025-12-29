import unittest
import random
from zuma import Level
from zuma import Ball
from zuma import settings
from zuma import spiral


class TestLevelGenerateChainLength(unittest.TestCase):
    def test_generate_chain_length(self):
        lvl = Level(1)
        expected = lvl.config.get(
            "initial_balls", settings.LEVELS[1]['initial_balls']
            )
        self.assertIsInstance(lvl.chain, list)
        self.assertEqual(len(lvl.chain), expected)


class TestLevelUpdate(unittest.TestCase):
    def test_update_moves_chain_and_decreases_timer(self):
        lvl = Level(1)
        if not lvl.chain:
            self.skipTest("no balls generated")
        t_before = lvl.chain[0].t
        time_before = lvl.time_remaining
        lvl.update(1.0)
        self.assertAlmostEqual(
            lvl.time_remaining, max(0.0, time_before - 1.0)
            )
        self.assertNotAlmostEqual(lvl.chain[0].t, t_before)


class TestLevelActivatePowerup(unittest.TestCase):
    def test_activate_powerup_adds_active_powerup(self):
        lvl = Level(1)
        lvl.activate_powerup("slow")
        self.assertTrue(any(p["type"] == "slow" for p in lvl.active_powerups))
        self.assertTrue(all("remaining" in p for p in lvl.active_powerups))


if __name__ == '__main__':
    unittest.main()