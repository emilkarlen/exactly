import unittest

from shellcheck_lib_test.cli.execution_mode.help import argument_parsing


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
