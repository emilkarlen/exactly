import unittest

from . import execution_mode
from . import default_main_program


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(execution_mode.suite())
    ret_val.addTest(default_main_program.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
