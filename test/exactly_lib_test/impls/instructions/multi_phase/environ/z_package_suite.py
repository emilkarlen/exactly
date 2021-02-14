import unittest

from exactly_lib_test.impls.instructions.multi_phase.environ import common, non_setup_phase, setup_phase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        common.suite(),
        non_setup_phase.suite(),
        setup_phase.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
