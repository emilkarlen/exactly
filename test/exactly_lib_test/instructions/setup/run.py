import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.setup import run as sut
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.run_instruction_test import \
    suite_for, \
    Configuration
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: asrt.ValueAssertion = asrt.is_empty_sequence):
        return Expectation(main_result=sh_assertions.is_hard_error(),
                           symbol_usages=symbol_usages)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
