import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert import change_dir as sut
from exactly_lib_test.impls.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.impls.instructions.before_assert.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: Assertion,
                                                     symbol_usages: Assertion = asrt.is_empty_sequence):
        return Expectation(main_side_effects_on_tcds=side_effects_check,
                           symbol_usages=symbol_usages)

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=asrt_sh.is_hard_error())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
