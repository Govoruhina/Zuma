import unittest

import pytest
from zuma import Level
from zuma.config import PowerUp, POWERUP_DURATION, POWERUP_SLOW_FACTOR

class DummyBall:
    def __init__(self, t=0.0):
        self.t = t
        self.last_update_speed = None
        self.update_calls = 0

    def update(self, dt, speed=None):
        # сохраняем скорость, инкрементируем т симулятивно
        self.last_update_speed = speed
        self.update_calls += 1
        # имитируем изменение т как реальный шар
        if speed is not None:
            self.t += dt * speed
        else:
            self.t += dt


def test_activate_powerup_adds_entry():
    lvl = Level(1)
    # очистим цепочку, т.к. нам не нужны реальные Балл-ы
    lvl.chain = []
    assert lvl.active_powerups == []

    lvl.activate_powerup(PowerUp.TYPE_SLOW)
    assert len(lvl.active_powerups) == 1
    p = lvl.active_powerups[0]
    assert p["type"] == PowerUp.TYPE_SLOW
    # ремаининг должно быть равно константе ПОВЕРУП_ДУРАТИОН
    assert pytest.approx(p["remaining"], rel=1e-3) == POWERUP_DURATION


def test_slow_powerup_reduces_chain_update_speed():
    lvl = Level(1)
    # подменим цепочку одним думмй-мячом
    dummy = DummyBall(t=0.0)
    lvl.chain = [dummy]

    # установим базовую скорость в некий известный валуе
    lvl.spiral_speed = 10.0
    lvl.base_spiral_speed = 10.0

    # активируем замедление
    lvl.activate_powerup(PowerUp.TYPE_SLOW)
    # сделаем один апдейт с дт=1.0
    lvl.update(1.0)

    # ожидаем, что переданная скорость равна спирал_спеед * ПОВЕРУП_СЛОВ_ФАКТОР
    expected = 10.0 * float(POWERUP_SLOW_FACTOR)
    assert dummy.update_calls == 1
    assert pytest.approx(dummy.last_update_speed, rel=1e-6) == expected


def test_reverse_powerup_inverts_chain_direction():
    lvl = Level(1)
    dummy = DummyBall(t=0.0)
    lvl.chain = [dummy]

    lvl.spiral_speed = 7.0
    lvl.base_spiral_speed = 7.0

    lvl.activate_powerup(PowerUp.TYPE_REVERSE)
    lvl.update(0.5)  # полсекунды, но нас интересует скорость

    # для обратный ход скорость должна быть отрицательной (обратный ход)
    assert dummy.update_calls == 1
    assert dummy.last_update_speed < 0.0
    # абсолютная величина скорости должна быть басе * 1.0 (реверсе_фактор == -1)
    assert pytest.approx(abs(dummy.last_update_speed), rel=1e-6) == 7.0


def test_powerup_expires_and_speed_restored():
    lvl = Level(1)
    dummy = DummyBall(t=0.0)
    lvl.chain = [dummy]

    lvl.spiral_speed = 5.0
    lvl.base_spiral_speed = 5.0

    # активируем замедление, затем симулируем время > ПОВЕРУП_ДУРАТИОН
    lvl.activate_powerup(PowerUp.TYPE_SLOW)
    # шаги: уменьшение ремаининг — вызываем обновление с суммой дт > ПОВЕРУП_ДУРАТИОН
    total = POWERUP_DURATION + 0.5
    # можно разделить на два кадра
    lvl.update(total / 2.0)
    lvl.update(total / 2.0)

    # теперь активе_поверупс должен быть пуст
    assert all(p["remaining"] > 0 for p in lvl.active_powerups) == False or len(lvl.active_powerups) == 0

    # при следующем обновление скорость должна быть восстановлена до базовой (без замедление)
    dummy.last_update_speed = None
    lvl.update(0.2)
    assert dummy.last_update_speed is not None
    # ожидаем близко к базовой (без применения ПОВЕРУП_СЛОВ_ФАКТОР)
    assert pytest.approx(dummy.last_update_speed, rel=1e-6) == pytest.approx(5.0 * 1.0)

if __name__ == "__main__":
    unittest.main()