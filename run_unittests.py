import os
import sys
import unittest


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    unit_tests_dir = os.path.join(base_dir, "tests")

    # Енсуре проджект роот ис импортабле (фор `зума.*`).
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=unit_tests_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()


