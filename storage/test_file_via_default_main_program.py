import unittest

from exactly_lib.default.default_main_program_setup import default_main_program

TEST_CASE_FILE = '/Users/emil/vcs/exactly/0/err_msg_tests/source-file-info/syntax-error-in-stand-alone-case.case'


class TC(unittest.TestCase):
    def runTest(self):
        main_program = default_main_program()
        exit_code = main_program.execute([TEST_CASE_FILE])
        print(str(exit_code))
