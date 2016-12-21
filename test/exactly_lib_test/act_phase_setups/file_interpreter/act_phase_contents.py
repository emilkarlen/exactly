import unittest

from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfiguration
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_line_source as single_line_source, \
    test_validation_for_single_file_rel_home as single_file_rel_home


def suite() -> unittest.TestSuite:
    tests = []
    configuration = TheConfiguration()
    tests.append(single_line_source.suite_for(configuration))
    tests.append(single_file_rel_home.suite_for(configuration))
    return unittest.TestSuite(tests)
