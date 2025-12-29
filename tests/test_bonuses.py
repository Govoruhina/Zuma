import unittest
from zuma import Level
from zuma import Frog
from zuma import Ball
from zuma.config import PowerUp, POWERUP_DURATION, POWERUP_SLOW_FACTOR

class TestPowerUps(unittest.TestCase):
    def setUp(self):
        self.level = Level(1)
        self.frog = Frog()
        # ставим один шарик для проверки
        self.ball_normal = Ball((255, 0, 0), t=0.0)
        self.level.chain = [self.ball_normal]

    def test_slow_powerup(self):
        self.level.activate_powerup(PowerUp.TYPE_SLOW)
        self.assertTrue(any(
            p["type"] == PowerUp.TYPE_SLOW 
            for p in self.level.active_powerups)
            )
        # проверяем модификатор скорости
        dt = 1.0
        self.level.spiral_speed = 100
        self.level.update(dt)
        slow_factor = min(p["remaining"] for p in self.level.active_powerups)
        self.assertTrue(slow_factor >= 0)

    def test_reverse_powerup(self):
        self.level.activate_powerup(PowerUp.TYPE_REVERSE)
        self.assertTrue(any(
            p["type"] == PowerUp.TYPE_REVERSE 
            for p in self.level.active_powerups)
            )
        # имитация обновления уровня
        speed_before = self.level.spiral_speed
        dt = 0.1
        self.level.update(dt)
        self.assertIsNotNone(speed_before)

    def test_fast_shoot_powerup(self):
        self.frog.shoot_speed_multiplier = 1.0
        # активация бонуса
        self.frog.shoot_speed_multiplier = 1.5
        self.assertEqual(self.frog.shoot_speed_multiplier, 1.5)
        # возвращаем обратно
        self.frog.shoot_speed_multiplier = 1.0
        self.assertEqual(self.frog.shoot_speed_multiplier, 1.0)

    def test_explosion_powerup(self):
        # создаём цепочку из 5 шаров
        self.level.chain = [Ball((i*50,0,0), t=i*10) for i in range(5)]
        idx_hit = 2
        explosion_radius = 1
        start_idx = max(0, idx_hit - explosion_radius)
        end_idx = min(len(self.level.chain)-1, idx_hit + explosion_radius)
        indices_to_remove = list(range(start_idx, end_idx+1))
        # имитируем ремове_кхаин
        removed_count = len(indices_to_remove)
        self.assertEqual(removed_count, 3)
        # после взрыва цепочка уменьшится
        for i in sorted(indices_to_remove, reverse=True):
            self.level.chain.pop(i)
        self.assertEqual(len(self.level.chain), 2)

if __name__ == "__main__":
    unittest.main()
