import unittest

from exactly_lib_test.execution import test_execution_directory_structure, \
    test_single_instruction_executor, \
    test_phase_step_execution
from exactly_lib_test.execution import partial_execution
from exactly_lib_test.execution import full_execution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_single_instruction_executor.suite())
    ret_val.addTest(test_phase_step_execution.suite())
    ret_val.addTest(test_execution_directory_structure.suite())
    ret_val.addTest(partial_execution.suite())
    ret_val.addTest(full_execution.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
