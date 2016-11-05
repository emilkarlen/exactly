import unittest

from exactly_lib_test.execution.instruction_execution import phase_step_execution, single_instruction_executor


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(single_instruction_executor.suite())
    ret_val.addTest(phase_step_execution.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
