import unittest
from unittest.mock import patch

from zuma import Game
from zuma import Ball
from zuma import Frog


class TestGameStartLevel(unittest.TestCase):

    def test_game_start_level_creates_level_and_sets_state(self):
        g = Game()
        g.start_level(1)

        self.assertEqual(g.state, "playing")
        self.assertIsNotNone(g.level)
        self.assertIsInstance(g.frog, Frog)
        self.assertEqual(g.score, 0)


class TestGamePowerUpCollision(unittest.TestCase):

    @patch("zuma.game.check_collision", return_value=0)
    def test_game_picks_up_powerup_on_collision(self, mock_collision):
        g = Game()
        g.start_level(1)

        pu_ball = Ball(color=(1, 2, 3), t=0.0, ball_type="slow")
        g.level.chain.insert(0, pu_ball)

        class DummyBall:
            def __init__(self):
                self.pos = [0.0, 0.0]
                self.dx = 0.0
                self.dy = 0.0
                self.speed = 1.0
                self.color = (10, 10, 10)
                self.type = "normal"

            def update(self, dt):
                pass

            def is_offscreen(self):
                return False

        db = DummyBall()
        g.flying_balls.append(db)

        before_score = g.score
        before_chain_len = len(g.level.chain)

        g.update(0.016)

        self.assertGreaterEqual(g.score, before_score + 150)
        self.assertNotIn(db, g.flying_balls)
        self.assertEqual(len(g.level.chain), before_chain_len - 1)
        self.assertTrue(
            any(p["type"] == "slow" for p in g.level.active_powerups)
        )


if __name__ == "__main__":
    unittest.main()
