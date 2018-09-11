import unittest

from exactly_lib_test.act_phase_setups.util.executor_made_of_parts import main


def suite() -> unittest.TestSuite:
    return main.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
