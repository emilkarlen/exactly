from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
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
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.util.cli_syntax.elements import argument as a


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(embryo_parser(instruction_name),
                                       spe_parts.ResultAndStderrTranslator())


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(instruction_name,
                                             program_parser())


def program_parser() -> Parser[ProgramResolver]:
    return parse_program.program_parser()


NON_ASSERT_PHASE_DESCRIPTION_REST = """\
It is considered an error if the program exits with a non-zero exit code.
"""


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str = 'Runs a ' + types.PROGRAM_TYPE_INFO.singular_name,
                 description_rest_text: str = None):
        self.description_rest_text = description_rest_text
        super().__init__(name, dict())
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def main_description_rest(self) -> list:
        if self.description_rest_text:
            return self._paragraphs(self.description_rest_text)
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument),
            ]),
        ]

    def see_also_targets(self) -> list:
        name_and_cross_ref_list = [
            types.PROGRAM_TYPE_INFO,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
        ]
        return cross_reference_id_list(name_and_cross_ref_list)
