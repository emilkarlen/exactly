import unittest

from exactly_lib_test.execution.partial_execution import \
    act_phase_tests, \
    instruction_environment, \
    deletion_of_eds, \
    phase_step_sequence


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(act_phase_tests.suite())
    ret_val.addTest(instruction_environment.suite())
    ret_val.addTest(deletion_of_eds.suite())
    ret_val.addTest(phase_step_sequence.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
