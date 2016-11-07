import unittest

from exactly_lib_test.instructions.assert_.test_resources import instruction_check_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_check_test.suite())
    return ret_val


def run_suite():
    unittest.TextTestRunner().run(suite())


if __name__ == '__main__':
    run_suite()
