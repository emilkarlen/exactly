from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions import path
from exactly_lib.definitions import syntax_descriptions
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.symbol.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse import token
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.DATA,
                         syntax_elements.STRING_SYNTAX_ELEMENT)
        the_string_type = 'the ' + types.STRING_TYPE_INFO.singular_name
        self._tp = TextParser({
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'list_type': formatting.keyword(types.LIST_TYPE_INFO.name.singular),
            'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
            'A_ref_to_symbol_w_string_conversion': types.a_ref_to_a_symbol_w_string_conversion__sentence(),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'CHR': 'CHARACTER',
            'whitespace': misc_texts.WHITESPACE,
            'SOFT_Q': token.SOFT_QUOTE_CHAR,
            'HARD_Q': token.HARD_QUOTE_CHAR,

            'soft_quotes': formatting.concept(syntax_descriptions.SOFT_QUOTE_NAME.plural),
            'hard_quotes': formatting.concept(syntax_descriptions.HARD_QUOTE_NAME.plural),
            'Sym_refs_are_substituted': syntax_descriptions.symbols_are_substituted_in(the_string_type),
            'Sym_refs_are_not_substituted': syntax_descriptions.symbols_are_not_substituted_in(the_string_type),
            'REL_CD_OPTION': path.REL_CWD_OPTION,
        })

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            InvokationVariant(self._tp.format('{CHR}...'),
                              self._tp.fnap(_DESCRIPTION_OF_NAKED)),
            InvokationVariant(self._tp.format('{SOFT_Q}{CHR}...{SOFT_Q}'),
                              self._tp.fnap(_DESCRIPTION_OF_SOFT_Q)),
            InvokationVariant(self._tp.format('{HARD_Q}{CHR}...{HARD_Q}'),
                              self._tp.fnap(_DESCRIPTION_OF_HARD_Q)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            self._symbol_reference_sed(),
        ]

    def main_description_rest_paragraphs(self) -> list:
        return []

    def see_also_targets(self) -> list:
        info_refs = cross_reference_id_list([
            syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
            types.STRING_TYPE_INFO,
            types.LIST_TYPE_INFO,
            types.PATH_TYPE_INFO,
            concepts.SYMBOL_CONCEPT_INFO,
        ])
        plain_refs = [
            define_symbol.DEFINE_SYMBOL_INSTRUCTION_CROSS_REFERENCE,
        ]
        return info_refs + plain_refs

    def _symbol_reference_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.argument.name,
                                        self._tp.fnap(_SYMBOL_REFERENCE_DESCRIPTION))

    @staticmethod
    def _cl_arguments() -> list:
        return [
            a.Choice.of_single_argument_choices(
                a.Multiplicity.ZERO_OR_MORE,
                [
                    syntax_elements.STRING_SYNTAX_ELEMENT.argument,
                    syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.argument,
                ]),
        ]


DOCUMENTATION = _Documentation()

_DESCRIPTION_OF_NAKED = """\
A "naked" sequence of characters.


{CHR} may not be {whitespace}.


{Sym_refs_are_substituted}
"""

_DESCRIPTION_OF_SOFT_Q = """\
Characters surrounded by {soft_quotes} ({SOFT_Q}).


{Sym_refs_are_substituted}
"""

_DESCRIPTION_OF_HARD_Q = """\
Characters surrounded by {hard_quotes} ({HARD_Q}).


{Sym_refs_are_not_substituted}
"""

_SYMBOL_REFERENCE_DESCRIPTION = """\
{A_ref_to_symbol_w_string_conversion}


An empty {list_type} value is rendered as an empty {string_type}.


A non-empty {list_type} value is rendered by separating the elements with a single space.


A {path_type} value is rendered as absolute paths (even if relativity is {REL_CD_OPTION}).
"""
