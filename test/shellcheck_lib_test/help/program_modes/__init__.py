import unittest

from shellcheck_lib_test.help.program_modes import test_case


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
