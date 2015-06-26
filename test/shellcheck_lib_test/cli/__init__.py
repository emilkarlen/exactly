import unittest

from . import execution_mode
from . import default


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(execution_mode.suite())
    ret_val.addTest(default.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
