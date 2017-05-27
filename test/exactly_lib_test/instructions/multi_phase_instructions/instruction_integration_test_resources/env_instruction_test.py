import unittest

from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, conf: ConfigurationBase):
        super().__init__(conf)
        self.conf = conf


class TestSet(TestCaseBase):
    def runTest(self):
        instruction_argument = 'name = value'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            environ = {}
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(environ=environ),
                self.conf.expect_success())
            self.assertEqual(environ,
                             {'name': 'value'})


class TestUnsetExistingVariable(TestCaseBase):
    def runTest(self):
        instruction_argument = 'unset a'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            environ = {'a': 'A', 'b': 'B'}
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(environ=environ),
                self.conf.expect_success())
            self.assertEqual(environ,
                             {'b': 'B'})


class TestUnsetNonExistingVariable(TestCaseBase):
    def runTest(self):
        instruction_argument = 'unset non_existing_variable'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            environ = {'a': 'A'}
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(environ=environ),
                self.conf.expect_success())
            self.assertEqual(environ,
                             {'a': 'A'})


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSet,
                               TestUnsetExistingVariable,
                               TestUnsetNonExistingVariable,
                           ])
