import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.setup import new_dir as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import new_dir_instruction_test
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.new_dir_instruction_test import \
    Configuration
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return Expectation(main_result=sh_check.is_hard_error(),
                           symbol_usages=symbol_usages)


def suite() -> unittest.TestSuite:
    return new_dir_instruction_test.suite_for(TheConfiguration())


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.setup('instr-name'), source, arrangement, expectation)
