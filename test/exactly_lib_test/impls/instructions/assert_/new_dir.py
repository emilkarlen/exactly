import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_ import new_dir as sut
from exactly_lib_test.impls.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.new_dir_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self,
                                     symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_result=asrt_pfh.is_hard_error__with_arbitrary_message(),
                           symbol_usages=symbol_usages)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
