import unittest

from shellcheck_lib_test.execution.partial_execution import \
    act_phase_tests, \
    phase_step_sequence_tests, \
    deletion_of_eds


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(act_phase_tests.suite())
    ret_val.addTest(deletion_of_eds.suite())
    ret_val.addTest(phase_step_sequence_tests.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
