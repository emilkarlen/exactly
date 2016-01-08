import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.setup import change_dir as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.utils import SideEffectsCheck


class TheConfiguration(SetupConfigurationBase, Configuration):
    def description(self) -> Description:
        return sut.description('instruction name')

    def parser(self) -> SingleInstructionParser:
        return sut.Parser()

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: SideEffectsCheck):
        return Expectation(side_effects_check=side_effects_check)

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=sh_check.IsHardError())


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
