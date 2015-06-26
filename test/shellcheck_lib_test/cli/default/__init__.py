import unittest

from shellcheck_lib_test.cli.default import instruction_name_and_argument_splitter as splitter
from shellcheck_lib_test.cli.default import main_program_default


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(splitter.suite())
    ret_val.addTest(main_program_default.suite())
    return ret_val
