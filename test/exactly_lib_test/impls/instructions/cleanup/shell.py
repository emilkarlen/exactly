import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.cleanup import shell as sut
from exactly_lib_test.impls.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.impls.instructions.cleanup.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.shell_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(CleanupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=asrt_sh.is_hard_error())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
