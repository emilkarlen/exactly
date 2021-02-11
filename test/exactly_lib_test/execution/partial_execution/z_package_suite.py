import unittest

from exactly_lib_test.execution.partial_execution import \
    setup_settings_handler, \
    atc_execution, \
    instruction_environment, \
    propagation_of_instruction_settings, \
    deletion_of_sds, \
    propagation_of_symbols, \
    propagation_of_hds
from exactly_lib_test.execution.partial_execution.phase_step_sequence import z_package_suite as phase_step_sequence


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(setup_settings_handler.suite())
    ret_val.addTest(atc_execution.suite())
    ret_val.addTest(instruction_environment.suite())
    ret_val.addTest(propagation_of_instruction_settings.suite())
    ret_val.addTest(deletion_of_sds.suite())
    ret_val.addTest(phase_step_sequence.suite())
    ret_val.addTest(propagation_of_hds.suite())
    ret_val.addTest(propagation_of_symbols.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
