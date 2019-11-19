from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.instructions.multi_phase.utils import \
    instruction_from_parts_for_executing_program as spe_parts
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser
from exactly_lib.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             program_parser())


def program_parser() -> Parser[ProgramSdv]:
    return parse_program.program_parser()


NON_ASSERT_PHASE_DESCRIPTION_REST = """\
It is considered an error if the program exits with a non-zero exit code.
"""

NON_ASSERT_PHASE_SINGLE_LINE_DESCRIPTION = 'Runs {program_type:a/q}'.format_map({
    'program_type': types.PROGRAM_TYPE_INFO.name
})


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str,
                 description_rest_text: str = None):
        self.description_rest_text = description_rest_text
        super().__init__(name, {
            'program_type': types.PROGRAM_TYPE_INFO.name
        })
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def main_description_rest(self) -> List[ParagraphItem]:
        ret_val = []
        if self.description_rest_text:
            ret_val += self._tp.fnap(self.description_rest_text)
        ret_val += self._tp.fnap(_MAIN_DESCRIPTION_REST)
        return ret_val

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument),
            ]),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_ref_list = [
            types.PROGRAM_TYPE_INFO,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
        ]
        return cross_reference_id_list(name_and_cross_ref_list)


_MAIN_DESCRIPTION_REST = """\
The {program_type} must terminate.
"""
