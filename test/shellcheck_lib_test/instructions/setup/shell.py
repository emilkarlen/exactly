import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.setup import shell as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.shell_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase


class TheConfiguration(SetupConfigurationBase, Configuration):
    def parser(self) -> SingleInstructionParser:
        return sut.parser()

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=sh_check.IsHardError())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.description('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(suite_for(TheConfiguration()))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
