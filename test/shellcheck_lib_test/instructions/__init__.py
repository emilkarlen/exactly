import unittest

from shellcheck_lib_test.instructions import instruction_parser_using_argument_parser
from shellcheck_lib_test.instructions import assert_phase


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_parser_using_argument_parser.suite())
    ret_val.addTest(assert_phase.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
