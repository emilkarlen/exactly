import os
import pathlib
import unittest

from exactly_lib.default.default_main_program_setup import default_main_program, default_output

SRC_DIR = '/Users/emil/vcs/exactly/0/err_msg_tests/symbols/validation/illegal-type/'

TEST_CASE_FILE = '/home/karlen/vcs/exactly/0/err-msg-tests/instructions/create-file/dst-file-is-a-relative-dir--here.case'
CWD = str(pathlib.Path(TEST_CASE_FILE).parent)

# TEST_CASE_FILE = SRC_DIR + 'instruction-error-in-stand-alone-case.case'

# ARGS = [TEST_CASE_FILE]

SUITE_FILE = SRC_DIR + 'instruction-error-of-case-instruction-in-suite.suite'

EMPTY_CASE = SRC_DIR + 'empty.case'

ARGS = [TEST_CASE_FILE
        ]

_ARGS = [
    '--act',
    '/Users/emil/vcs/exactly/0/err-msg-tests/symbols/validation/ref-to-undef-symbol.case',
        ]


class TC(unittest.TestCase):
    def runTest(self):
        if CWD:
            os.chdir(CWD)

        main_program = default_main_program()
        exit_code = main_program.execute(ARGS, default_output())
        print(str(exit_code))
