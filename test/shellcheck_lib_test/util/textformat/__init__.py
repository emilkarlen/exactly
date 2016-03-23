import unittest

from shellcheck_lib_test.util.textformat import formatting, parse, utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(formatting.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(utils.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
