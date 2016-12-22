import unittest

from exactly_lib_test.act_phase_setups.file_interpreter import act_phase_contents
from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfiguration
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import suite_for_execution


def suite() -> unittest.TestSuite:
    tests = []
    the_configuration = TheConfiguration()
    tests.append(single_file_rel_home.suite_for(the_configuration))
    tests.append(suite_for_execution(the_configuration))
    return unittest.TestSuite(tests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
