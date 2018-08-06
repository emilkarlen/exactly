import unittest

from exactly_lib.default.default_main_program_setup import default_main_program

SRC_DIR = '/Users/emil/vcs/exactly/0/err_msg_tests/symbols/validation/illegal-type/'

TEST_CASE_FILE = SRC_DIR + 'expecting-file-matcher.case'

# TEST_CASE_FILE = SRC_DIR + 'instruction-error-in-stand-alone-case.case'

# ARGS = [TEST_CASE_FILE]

SUITE_FILE = SRC_DIR + 'instruction-error-of-case-instruction-in-suite.suite'

EMPTY_CASE = SRC_DIR + 'empty.case'

ARGS = [TEST_CASE_FILE
        ]


class TC(unittest.TestCase):
    def runTest(self):
        main_program = default_main_program()
        exit_code = main_program.execute(ARGS)
        print(str(exit_code))
