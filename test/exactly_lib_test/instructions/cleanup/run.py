import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup import run as sut
from exactly_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.instructions.cleanup.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.run_instruction_test import \
    suite_for, Configuration
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TheConfiguration(CleanupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        return Expectation(main_result=sh_assertions.is_hard_error(),
                           symbol_usages=symbol_usages)


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
