from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.before_assert import new_dir as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.new_dir_instruction_test import \
    Configuration, suite_for
from shellcheck_lib_test.instructions.test_resources import sh_check__va


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def parser(self) -> SingleInstructionParser:
        return self.instruction_setup()

    def description(self) -> Description:
        return self.instruction_setup().description

    def expect_failure_to_create_dir(self):
        return Expectation(main_result=sh_check__va.is_hard_error())


def suite():
    return suite_for(TheConfiguration())
