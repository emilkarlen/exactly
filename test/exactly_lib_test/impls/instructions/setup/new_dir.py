import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.setup import new_dir as sut
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources import phase_integration
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.phase_integration import \
    Configuration
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: Assertion = asrt.is_empty_sequence):
        return Expectation(main_result=asrt_sh.is_hard_error(),
                           symbol_usages=symbol_usages)


def suite() -> unittest.TestSuite:
    return phase_integration.suite_for(TheConfiguration())
