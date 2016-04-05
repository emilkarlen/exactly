import unittest

from shellcheck_lib_test.default import default_main_program
from shellcheck_lib_test.default import instruction_name_and_argument_splitter as splitter


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(splitter.suite())
    ret_val.addTest(default_main_program.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
