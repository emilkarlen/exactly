import unittest

from shellcheck_lib_test.execution.partial_execution.phase_step_sequence import \
    full_successful, \
    pre_eds_validation_error, \
    other_scenarios


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(full_successful.suite())
    ret_val.addTest(pre_eds_validation_error.suite())
    ret_val.addTest(other_scenarios.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
