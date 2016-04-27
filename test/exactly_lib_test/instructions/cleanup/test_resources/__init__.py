import unittest

from exactly_lib_test.instructions.cleanup.test_resources import instruction_check_test


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_check_test.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
