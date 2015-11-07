import unittest

from shellcheck_lib_test.instructions.utils import file_ref
from shellcheck_lib_test.instructions.utils import parse_utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(file_ref.suite())
    ret_val.addTest(parse_utils.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
