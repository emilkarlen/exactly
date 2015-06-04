import unittest

from shellcheck_lib_test.cli import parse_command_line_and_execute_test_case, argument_parsing


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(parse_command_line_and_execute_test_case.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
