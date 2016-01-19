import unittest

from shellcheck_lib.instructions.assert_phase import shell as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.assert_phase.test_resources.configuration import AssertConfigurationBase
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.shell_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.check_description import suite_for_description


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_check.is_fail())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(suite_for(TheConfiguration()))
    ret_val.addTest(suite_for_description(sut.TheDescription('instruction-name')))
    return ret_val


if __name__ == '__main__':
    unittest.main()
