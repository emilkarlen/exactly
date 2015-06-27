import unittest

from shellcheck_lib_test.default import instruction_name_and_argument_splitter as splitter


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(splitter.suite())
    return ret_val
