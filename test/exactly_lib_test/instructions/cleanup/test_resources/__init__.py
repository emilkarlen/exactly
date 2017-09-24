import unittest

from exactly_lib_test.instructions.cleanup.test_resources import instruction_check_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_check_test.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
