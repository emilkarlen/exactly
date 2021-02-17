import unittest

from exactly_lib_test.execution.full_execution import \
    propagation_of_timeout_to_phases, \
    propagation_of_predefined_properties_to_phases, \
    propagation_of_mem_buff_size_to_phases, translation_of_partial_result_to_full_result
from exactly_lib_test.execution.full_execution.environment import z_package_suite as environment
from exactly_lib_test.execution.full_execution.execution_mode import z_package_suite as execution_mode


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(translation_of_partial_result_to_full_result.suite())
    ret_val.addTest(environment.suite())
    ret_val.addTest(execution_mode.suite())
    ret_val.addTest(propagation_of_timeout_to_phases.suite())
    ret_val.addTest(propagation_of_predefined_properties_to_phases.suite())
    ret_val.addTest(propagation_of_mem_buff_size_to_phases.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
