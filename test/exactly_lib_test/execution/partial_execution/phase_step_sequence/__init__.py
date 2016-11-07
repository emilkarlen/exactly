import unittest

from exactly_lib_test.execution.partial_execution.phase_step_sequence import \
    full_successful, \
    pre_sds_validation_error, \
    validate_post_setup, \
    other_scenarios, \
    act_phase_handling_failure


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(full_successful.suite())
    ret_val.addTest(pre_sds_validation_error.suite())
    ret_val.addTest(validate_post_setup.suite())
    ret_val.addTest(act_phase_handling_failure.suite())
    ret_val.addTest(other_scenarios.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
