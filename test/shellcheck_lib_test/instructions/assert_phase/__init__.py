import unittest

from shellcheck_lib_test.instructions.assert_phase import exitcode
from shellcheck_lib_test.instructions.assert_phase import file
from shellcheck_lib_test.instructions.assert_phase import stdout_stderr


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(exitcode.suite())
    ret_val.addTest(file.suite())
    ret_val.addTest(stdout_stderr.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
