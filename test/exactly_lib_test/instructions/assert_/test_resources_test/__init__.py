import unittest

from exactly_lib_test.instructions.assert_.test_resources_test import instruction_check_test


def suite() -> unittest.TestSuite:
    return instruction_check_test.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
