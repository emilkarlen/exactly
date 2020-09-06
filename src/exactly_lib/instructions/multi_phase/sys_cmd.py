from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithSplittedPartsForRestDocBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import misc_texts
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
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import CurrentLineMustNotBeEmptyExceptForSpace
from exactly_lib.test_case_utils.program.parse import parse_system_program
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(
        instruction_name,
        CurrentLineMustNotBeEmptyExceptForSpace(
            parse_system_program.program_parser(),
            'Missing PROGRAM-NAME',
        )
    )


_SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS = misc_texts.SYSTEM_CMD_SINGLE_LINE_DESCRIPTION

SINGLE_LINE_DESCRIPTION_FOR_ASSERT_PHASE_INSTRUCTION = (
        _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS +
        ', and {} iff its {} is 0'.format(exit_values.EXECUTION__PASS.exit_identifier,
                                          misc_texts.EXIT_CODE)
)


class TheInstructionDocumentationBase(InstructionDocumentationWithSplittedPartsForRestDocBase,
                                      IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str):
        super().__init__(name, {
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
            'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
        })
        self.__single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self.__single_line_description

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory,
                syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.zero_or_more,
            ],
                []),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT,
        ])


class DescriptionForNonAssertPhaseInstruction(TheInstructionDocumentationBase):
    def __init__(self, name: str):
        super().__init__(name,
                         _SINGLE_LINE_DESCRIPTION_FOR_NON_ASSERT_PHASE_INSTRUCTIONS)

    def outcome(self) -> SectionContents:
        return self._tp.section_contents(_OUTCOME__NON_ASSERT_PHASE)


_OUTCOME__NON_ASSERT_PHASE = """\
The result is {HARD_ERROR} if the program exits with a non-zero exit code.
"""
