import unittest

from shellcheck_lib_test.instructions.utils import parse_utils
from shellcheck_lib_test.instructions.utils import file_ref
from shellcheck_lib_test.instructions.utils import parse_file_ref
from shellcheck_lib_test.instructions.utils import parse_here_document


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_utils.suite())
    ret_val.addTest(file_ref.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
