import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert import new_dir as sut
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.new_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case_utils.test_resources import sh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return Expectation(main_result=sh_assertions.is_hard_error(),
                           symbol_usages=symbol_usages)
