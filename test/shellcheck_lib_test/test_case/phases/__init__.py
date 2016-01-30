import unittest

from shellcheck_lib_test.test_case.phases import common


def suite() -> unittest.TestSuite:
    return common.suite()


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
