from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(syntax_elements.LIST_SYNTAX_ELEMENT)

        self._tp = TextParser({
            'list_type': types.LIST_TYPE_INFO.name,
            'A_ref_to_symbol_w_string_conversion': types.a_ref_to_a_symbol_w_string_conversion__sentence(),
        })

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args(self._cl_arguments())
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            self._symbol_reference_sed(),
        ]

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return []

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        info_refs = cross_reference_id_list([
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
            concepts.SYMBOL_CONCEPT_INFO,
            types.LIST_TYPE_INFO,
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

_SYMBOL_REFERENCE_DESCRIPTION = """\
{A_ref_to_symbol_w_string_conversion}


If it is a {list_type}, it is concatenated with the surrounding elements -
{list_type:s} cannot be nested.
"""
