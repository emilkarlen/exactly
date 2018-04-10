from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions import formatting
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types, concepts
from exactly_lib.definitions.test_case.instructions import define_symbol
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.DATA,
                         syntax_elements.LIST_SYNTAX_ELEMENT)

        self._tp = TextParser({
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'list_type': formatting.keyword(types.LIST_TYPE_INFO.name.singular),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
        })

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            self._symbol_reference_sed(),
        ]

    def main_description_rest_paragraphs(self) -> list:
        return []

    def see_also_targets(self) -> list:
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
    def _cl_arguments() -> list:
        return [
            a.Choice(a.Multiplicity.ZERO_OR_MORE,
                     [
                         syntax_elements.STRING_SYNTAX_ELEMENT.argument,
                         syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.argument,
                     ]),
        ]


DOCUMENTATION = _Documentation()

_SYMBOL_REFERENCE_DESCRIPTION = """\
A reference to a {symbol} defined as either {string_type} or {list_type}.


If it is a {list_type}, it is concatenated with the surrounding elements -
lists cannot be nested.
"""
