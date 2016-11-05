import unittest

from exactly_lib_test.execution import full_execution
from exactly_lib_test.execution import instruction_execution
from exactly_lib_test.execution import partial_execution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(instruction_execution.suite())
    ret_val.addTest(partial_execution.suite())
    ret_val.addTest(full_execution.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
