import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert import run as sut
from exactly_lib_test.impls.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.impls.instructions.before_assert.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.run_instruction_test import \
    suite_for, Configuration
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_result=asrt_sh.is_hard_error(),
                           symbol_usages=symbol_usages)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
