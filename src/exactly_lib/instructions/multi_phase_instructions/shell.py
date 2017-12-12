from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help_texts.instruction_arguments import COMMAND_ARGUMENT
from exactly_lib.instructions.multi_phase_instructions.utils import \
    instruction_from_parts_for_executing_sub_process as spe_parts
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.processing.exit_values import EXECUTION__HARD_ERROR
from exactly_lib.test_case_utils.sub_proc.shell_program import ShellCommandSetupParser
from exactly_lib.util.cli_syntax.elements import argument as a


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             ShellCommandSetupParser())


_SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS = \
    "Executes a command using the current operating system's shell"

SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION = (
    "Executes a command using the current operating system's shell,"
    " and PASS if, and only if, its exit code is 0")


class TheInstructionDocumentationBase(InstructionDocumentationWithCommandLineRenderingAndSplittedPartsForRestDocBase,
                                      IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str):
        super().__init__(name, {
            'COMMAND': COMMAND_ARGUMENT.name,
            'HARD_ERROR': EXECUTION__HARD_ERROR.exit_identifier,
        })
        self.__single_line_description = single_line_description
        self.command_arg = COMMAND_ARGUMENT

    def single_line_description(self) -> str:
        return self.__single_line_description

    def _main_description_rest_body(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST_BODY)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.command_arg)]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.command_arg.name,
                                     self._paragraphs(_COMMAND_SYNTAX_ELEMENT_DESCRIPTION))
        ]


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name,
                         _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS)

    def _main_description_rest_prelude(self) -> list:
        return self._paragraphs(_NON_ASSERT_PHASE_REST_PRELUDE)


_MAIN_DESCRIPTION_REST_BODY = """\
Which commands are available and the syntax of them depends
on the current operating system's shell and environment.


The shell takes care of interpreting {COMMAND}, so all features of the
shell can be used.


Use of the {instruction_name} instruction is not portable since it
uses the current operating system environment's shell.


On POSIX, the shell defaults to /bin/sh.

On Windows, the COMSPEC environment variable specifies the default shell.
"""

_NON_ASSERT_PHASE_REST_PRELUDE = """\
The result is {HARD_ERROR} if {COMMAND} exits with a non-zero exit code.
"""

_COMMAND_SYNTAX_ELEMENT_DESCRIPTION = """\
Something that is understood by the current operating system's shell.


It is the literal text until end of line.
"""
