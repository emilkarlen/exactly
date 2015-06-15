import unittest

from shellcheck_lib_test.cli import main_program_default, argument_parsing


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(main_program_default.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
