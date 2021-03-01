from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions import path
from exactly_lib.definitions import syntax_descriptions
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.symbol import value_type
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse import token
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(syntax_elements.STRING_SYNTAX_ELEMENT)
        the_string_type = 'the ' + types.STRING_TYPE_INFO.singular_name
        non_str_types_w_str_conversion = value_type.sorted_types(
            set(value_type.VALUE_TYPES_W_STR_RENDERING) -
            {value_type.ValueType.STRING}
        )
        self._tp = TextParser({
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'symbol_reference': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            'type': concepts.TYPE_CONCEPT_INFO.name,
            'string_type': types.STRING_TYPE_INFO.name,
            'list_type': types.LIST_TYPE_INFO.name,
            'path_type': types.PATH_TYPE_INFO.name,

            'A_ref_to_symbol_w_string_conversion': types.a_ref_to_a_symbol_w_string_conversion__sentence(),
            'non_str_types_w_str_rendering': types.types__and_list(non_str_types_w_str_conversion),

            'soft_quote': syntax_descriptions.SOFT_QUOTE_NAME,
            'hard_quote': syntax_descriptions.HARD_QUOTE_NAME,
            'SOFT_Q': token.SOFT_QUOTE_CHAR,
            'HARD_Q': token.HARD_QUOTE_CHAR,
            'CHR': 'CHARACTER',
            'whitespace': misc_texts.WHITESPACE,

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

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            self._symbol_reference_sed(),
        ]

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return [
            self._tp.section(
                'Concatenation',
                _DESCRIPTION__CONCATENATION,
            ),
            self._tp.section(
                'Conversion of {non_str_types_w_str_rendering}',
                _DESCRIPTION__TYPE_CONVERSION,
            ),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
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
    def _cl_arguments() -> List[a.ArgumentUsage]:
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
Characters surrounded by {soft_quote:s/q} ({SOFT_Q}).


{Sym_refs_are_substituted}
"""

_DESCRIPTION_OF_HARD_Q = """\
Characters surrounded by {hard_quote:s/q} ({HARD_Q}).


{Sym_refs_are_not_substituted}
"""

_SYMBOL_REFERENCE_DESCRIPTION = """\
{A_ref_to_symbol_w_string_conversion}
"""

_DESCRIPTION__CONCATENATION = """\
{string_type:/u} fragments of the different forms may be concatenated
by putting them side by side (without intervening {whitespace}).
"""

_DESCRIPTION__TYPE_CONVERSION = """\
References to these {type:s} can be converted to {string_type:s},
either by putting the {symbol_reference} inside {soft_quote:s},
or by using a naked {symbol_reference} (in most places).


An empty {list_type:/q} is rendered as an empty {string_type}.


A non-empty {list_type:/q} is rendered by separating the elements with a single space.


{path_type:a/qu} is rendered as an absolute path (even if relativity is {REL_CD_OPTION}).
"""
