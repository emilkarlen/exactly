import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.setup import new_dir as sut
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    new_dir_instruction_test
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.new_dir_instruction_test import \
    Configuration
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_result=asrt_sh.is_hard_error(),
                           symbol_usages=symbol_usages)


def suite() -> unittest.TestSuite:
    return new_dir_instruction_test.suite_for(TheConfiguration())