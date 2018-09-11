import unittest

from exactly_lib_test.act_phase_setups.util.executor_made_of_parts import z_package_suite as executor_made_of_parts


def suite() -> unittest.TestSuite:
    return executor_made_of_parts.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
