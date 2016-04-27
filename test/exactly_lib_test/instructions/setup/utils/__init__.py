import unittest

from exactly_lib_test.instructions.setup.utils import instruction_utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_utils.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
