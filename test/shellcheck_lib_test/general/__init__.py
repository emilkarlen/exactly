import unittest

from shellcheck_lib_test.general import line_source


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(line_source.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
