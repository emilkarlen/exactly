from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions import syntax_descriptions
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.current_directory_and_path_type import def_instruction_rel_cd_description
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.test_case.instructions import define_symbol as syntax
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.table import TableCell
from . import type_setup, type_parser
from .type_setup import TypeSetup


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str):
        self.name = syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument
        self.string_value = syntax_elements.STRING_SYNTAX_ELEMENT.argument
        super().__init__(name,
                         {
                             'NAME': self.name.name,
                             'SYMBOL': concepts.SYMBOL_CONCEPT_INFO.name,
                         },
                         False)

    def single_line_description(self) -> str:
        return self._tp.format('Defines {SYMBOL:a}')

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(syntax.def_instruction_argument_syntax())
            )
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return ([
            SyntaxElementDescription(', '.join([syntax.TYPE_SYNTAX_ELEMENT,
                                                syntax.VALUE_SYNTAX_ELEMENT]),
                                     [self._types_table()]),

            rel_path_doc.path_element_with_all_relativities(
                _PATH_ARGUMENT.name,
                type_parser.REL_OPTION_ARGUMENT_CONFIGURATION.options.default_option,
                def_instruction_rel_cd_description(_PATH_ARGUMENT.name)),

            SyntaxElementDescription(self.string_value.name,
                                     self._tp.fnap(syntax_descriptions.STRING_SYNTAX_ELEMENT_DESCRIPTION)),

            SyntaxElementDescription(self.name.name,
                                     self._tp.fnap(syntax_descriptions.SYMBOL_NAME_SYNTAX_DESCRIPTION)),
        ])

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [concepts.SYMBOL_CONCEPT_INFO,
                               concepts.TYPE_CONCEPT_INFO,
                               concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
                               syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                               ]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    @staticmethod
    def _types_table() -> docs.ParagraphItem:
        def type_row(ts: TypeSetup) -> List[TableCell]:
            return [
                docs.text_cell(syntax_text(ts.type_info.identifier)),
                docs.text_cell(syntax_text(cl_syntax.cl_syntax_for_args(ts.value_arguments))),
            ]

        rows = [
            [
                docs.text_cell(syntax.TYPE_SYNTAX_ELEMENT),
                docs.text_cell(syntax.VALUE_SYNTAX_ELEMENT),
            ]
        ]

        rows += map(type_row, type_setup.TYPE_SETUPS_LIST)

        return docs.first_row_is_header_table(rows)


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

_MAIN_DESCRIPTION_REST = """\
Defines the symbol {NAME} to be a value of the given type.


{NAME} must not have been defined earlier.


The defined symbol is available in all following instructions and phases.
"""
