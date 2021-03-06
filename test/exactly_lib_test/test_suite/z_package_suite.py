import unittest

from exactly_lib_test.test_suite import enumeration, propagation_of_act_phase_setup_to_individual_test_cases
from exactly_lib_test.test_suite.case_instructions import z_package_suite as case_instructions
from exactly_lib_test.test_suite.file_reading import z_package_suite as file_reading
from exactly_lib_test.test_suite.instruction_set import z_package_suite as instruction_set
from exactly_lib_test.test_suite.processing import z_package_suite as processing
from exactly_lib_test.test_suite.reporters import z_package_suite as reporters


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(enumeration.suite())
    ret_val.addTest(file_reading.suite())
    ret_val.addTest(processing.suite())
    ret_val.addTest(instruction_set.suite())
    ret_val.addTest(propagation_of_act_phase_setup_to_individual_test_cases.suite())
    ret_val.addTest(reporters.suite())
    ret_val.addTest(case_instructions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
