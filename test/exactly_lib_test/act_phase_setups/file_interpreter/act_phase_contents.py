import unittest

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_line_source as single_line_source, \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())


def suite() -> unittest.TestSuite:
    tests = []
    configuration = TheConfiguration()
    tests.append(single_line_source.suite_for(configuration))
    tests.append(single_file_rel_home.suite_for(configuration))
    return unittest.TestSuite(tests)
