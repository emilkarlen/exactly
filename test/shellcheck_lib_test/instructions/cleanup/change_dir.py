from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.cleanup import change_dir as sut
from shellcheck_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.utils import SideEffectsCheck


class TheConfiguration(CleanupConfigurationBase, Configuration):
    def parser(self) -> SingleInstructionParser:
        return sut.Parser()

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: SideEffectsCheck):
        return Expectation(side_effects_check=side_effects_check)

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=sh_check.IsHardError())


def suite():
    return suite_for(TheConfiguration())
