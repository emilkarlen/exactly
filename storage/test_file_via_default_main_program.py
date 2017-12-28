import unittest

from exactly_lib.default.default_main_program_setup import default_main_program

SRC_DIR = '/Users/emil/vcs/exactly/0/err_msg_tests/source-file-info/'

TEST_CASE_FILE = SRC_DIR + 'syntax-error-in-stand-alone-case.case'

# TEST_CASE_FILE = SRC_DIR + 'instruction-error-in-stand-alone-case.case'

# ARGS = [TEST_CASE_FILE]

SUITE_FILE = SRC_DIR + 'instruction-error-of-case-instruction-in-suite.suite'

EMPTY_CASE = SRC_DIR + 'empty.case'

ARGS = ['--suite',
        SUITE_FILE,
        EMPTY_CASE
        ]


class TC(unittest.TestCase):
    def runTest(self):
        main_program = default_main_program()
        exit_code = main_program.execute(ARGS)
        print(str(exit_code))
