from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.cleanup import change_dir as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from shellcheck_lib_test.instructions.cleanup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.change_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import AdaptVa
from shellcheck_lib_test.test_resources.value_assertion import ValueAssertion


class TheConfiguration(CleanupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def parser(self) -> SingleInstructionParser:
        return self.instruction_setup()

    def description(self) -> Description:
        return self.instruction_setup().description

    def expect_successful_execution_with_side_effect(self,
                                                     side_effects_check: ValueAssertion):
        return Expectation(side_effects_check=AdaptVa(side_effects_check))

    def expect_target_is_not_a_directory(self):
        return Expectation(main_result=sh_check.IsHardError())


def suite():
    return suite_for(TheConfiguration())
