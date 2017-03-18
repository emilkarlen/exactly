import unittest

from exactly_lib_test.execution.instruction_execution.phase_step_executors import setup


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(setup.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
