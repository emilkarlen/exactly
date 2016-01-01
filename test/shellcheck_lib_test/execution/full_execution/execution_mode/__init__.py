import unittest

from shellcheck_lib_test.execution.full_execution.execution_mode import \
    normal, \
    skipped, \
    xfail


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(normal.suite())
    ret_val.addTest(skipped.suite())
    ret_val.addTest(xfail.suite())
    return ret_val


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
