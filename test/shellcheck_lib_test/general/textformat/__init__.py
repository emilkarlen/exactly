import unittest

from shellcheck_lib_test.general.textformat import formatting, parse


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(formatting.suite())
    ret_val.addTest(parse.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
