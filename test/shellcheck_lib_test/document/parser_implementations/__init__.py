import unittest

from shellcheck_lib_test.document.parser_implementations import instruction_parser_for_single_phase

from shellcheck_lib_test.document.parser_implementations import instruction_parser_using_argument_parser


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_parser_for_single_phase.suite())
    ret_val.addTest(instruction_parser_using_argument_parser.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
