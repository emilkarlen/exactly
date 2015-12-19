import unittest

from shellcheck_lib_test.general import line_source
from shellcheck_lib_test.general import monad
from shellcheck_lib_test.general import textformat


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(line_source.suite())
    ret_val.addTest(textformat.suite())
    ret_val.addTest(monad.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
