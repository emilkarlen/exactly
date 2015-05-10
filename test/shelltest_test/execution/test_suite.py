import unittest

from shelltest_test.execution import test_execution_directory_structure, \
    test_single_instruction_executor, \
    test_phase_step_execution
from shelltest_test.execution.test_execution_environment import test_suite as execution_environment_test_suite
from shelltest_test.execution.test_full_execution_sequence import test_suite as full_execution_test_suite


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_single_instruction_executor.suite())
    ret_val.addTest(test_phase_step_execution.suite())
    ret_val.addTest(test_execution_directory_structure.suite())
    ret_val.addTest(execution_environment_test_suite.suite())
    ret_val.addTest(full_execution_test_suite.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
