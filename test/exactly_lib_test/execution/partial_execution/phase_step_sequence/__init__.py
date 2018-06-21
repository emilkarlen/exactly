import unittest

from exactly_lib_test.execution.partial_execution.phase_step_sequence import \
    complete_successful, \
    symbol_validation_error, \
    pre_sds_validation_error, \
    validate_post_setup, \
    other_scenarios, \
    act_phase_handling_failure, \
    act_phase_symbol_handling, \
    action_to_check_output


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(complete_successful.suite())
    ret_val.addTest(symbol_validation_error.suite())
    ret_val.addTest(pre_sds_validation_error.suite())
    ret_val.addTest(validate_post_setup.suite())
    ret_val.addTest(act_phase_handling_failure.suite())
    ret_val.addTest(act_phase_symbol_handling.suite())
    ret_val.addTest(other_scenarios.suite())
    ret_val.addTest(action_to_check_output.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
