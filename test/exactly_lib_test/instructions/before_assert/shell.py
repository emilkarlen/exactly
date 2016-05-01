import unittest

from exactly_lib.instructions.before_assert import shell as sut
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.shell_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.instructions.test_resources import sh_check__va


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_check__va.is_hard_error())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
