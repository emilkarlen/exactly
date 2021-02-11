import unittest

from exactly_lib_test.impls.instructions.multi_phase.environ import test_suite


def suite() -> unittest.TestSuite:
    return test_suite.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
