from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithSplittedPartsForRestDocBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.multi_phase.utils import \
    instruction_from_parts_for_executing_program as spe_parts
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.processing.exit_values import EXECUTION__HARD_ERROR
from exactly_lib.test_case_utils.program.parse import parse_shell_command
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             parse_shell_command.program_parser())


_SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS = \
    "Executes a command using the current operating system's shell"

SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION = (
    "Executes a command using the current operating system's shell,"
    " and PASS if, and only if, its exit code is 0")


class TheInstructionDocumentationBase(InstructionDocumentationWithSplittedPartsForRestDocBase,
                                      IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str):
        super().__init__(name, {
            'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name,
            'HARD_ERROR': EXECUTION__HARD_ERROR.exit_identifier,
        })
        self.__single_line_description = single_line_description
        self.command_arg = instruction_arguments.COMMAND_ARGUMENT

    def single_line_description(self) -> str:
        return self.__single_line_description

    def _main_description_rest_body(self) -> list:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.command_arg)],
                []),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            SyntaxElementDescription(self.command_arg.name,
                                     self._tp.fnap(_COMMAND_SYNTAX_ELEMENT_DESCRIPTION))
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT,
        ])


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name,
                         _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS)

    def _main_description_rest_prologue(self) -> List[ParagraphItem]:
        return self._tp.fnap(_NON_ASSERT_PHASE_REST_PRELUDE)


_NON_ASSERT_PHASE_REST_PRELUDE = """\
The result is {HARD_ERROR} if {COMMAND} exits with a non-zero exit code.
"""

_COMMAND_SYNTAX_ELEMENT_DESCRIPTION = """\
Something that is understood by the current operating system's shell.


It is the literal text until end of line.
"""
