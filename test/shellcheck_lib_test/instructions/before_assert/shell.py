import unittest

from shellcheck_lib.instructions.before_assert import shell as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.shell_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources.check_description import suite_for_description


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_check__va.is_hard_error())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(suite_for(TheConfiguration()))
    ret_val.addTest(suite_for_description(sut.setup('instruction-name').description))
    return ret_val


if __name__ == '__main__':
    unittest.main()
