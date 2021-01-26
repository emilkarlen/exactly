from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithSplittedPartsForRestDocBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.impls.instructions.multi_phase.utils import \
    instruction_from_parts_for_executing_program as spe_parts, simple_proc_exe_help
from exactly_lib.impls.instructions.multi_phase.utils import run_assertions
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.impls.types.program.parse import parse_shell_command
from exactly_lib.processing import exit_values
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.document import SectionContents


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(
        instruction_name,
        parse_shell_command.program_parser()
    )


_SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS = \
    "Executes a command using the current operating system's shell"

SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION = run_assertions.single_line_description_as_assertion(
    _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS
)


class TheInstructionDocumentationBase(InstructionDocumentationWithSplittedPartsForRestDocBase,
                                      IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 phase_name: str,
                 single_line_description: str,
                 ):
        self._phase_name = phase_name
        self.command_arg = syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.argument
        super().__init__(name, {
            'COMMAND': self.command_arg.name,
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
            'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'EXIT_CODE': misc_texts.EXIT_CODE.singular,
        })
        self.__single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self.__single_line_description

    def _main_description_rest_body(self) -> list:
        return []

    def notes(self) -> SectionContents:
        return simple_proc_exe_help.notes_on_when_to_use_run_instruction()

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.command_arg)],
                []),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT.cross_reference_target,
            TestCasePhaseInstructionCrossReference(
                self._phase_name,
                instruction_names.RUN_INSTRUCTION_NAME,
            )
        ]


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self,
                 name: str,
                 phase_name: str,
                 ):
        super().__init__(name,
                         phase_name,
                         _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS)

    def outcome(self) -> SectionContents:
        return self._tp.section_contents(_OUTCOME__NON_ASSERT_PHASE)


_OUTCOME__NON_ASSERT_PHASE = """\
The result is {HARD_ERROR} if {COMMAND} exits with a non-zero {EXIT_CODE}.
"""
