import unittest

from exactly_lib_test.execution.full_execution import execution_mode
from exactly_lib_test.execution.full_execution import \
    test_translation_of_partial_result_to_full_result, \
    test_environment, \
    propagation_of_timeout_to_phases, \
    propagation_of_predefined_properties_to_phases


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(test_translation_of_partial_result_to_full_result.Test))
    ret_val.addTest(unittest.makeSuite(test_environment.Test))
    ret_val.addTest(execution_mode.suite())
    ret_val.addTest(propagation_of_timeout_to_phases.suite())
    ret_val.addTest(propagation_of_predefined_properties_to_phases.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
