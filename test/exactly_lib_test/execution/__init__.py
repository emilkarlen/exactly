import unittest

from exactly_lib_test.execution import full_execution
from exactly_lib_test.execution import instruction_execution
from exactly_lib_test.execution import partial_execution
from exactly_lib_test.execution import symbols_handling


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(symbols_handling.suite())
    ret_val.addTest(instruction_execution.suite())
    ret_val.addTest(partial_execution.suite())
    ret_val.addTest(full_execution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
