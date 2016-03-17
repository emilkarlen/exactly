import unittest

from shellcheck_lib_test.util import functional, line_source, monad, textformat


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(functional.suite())
    ret_val.addTest(monad.suite())
    ret_val.addTest(line_source.suite())
    ret_val.addTest(textformat.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
