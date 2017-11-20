from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_element, types, concepts
from exactly_lib.help_texts.instruction_arguments import SYMBOL_SYNTAX_ELEMENT_NAME
from exactly_lib.help_texts.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.names import formatting
from exactly_lib.instructions.utils.documentation import documentation_text
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(TypeCategory.DATA,
                         syntax_element.LIST_SYNTAX_ELEMENT)

        self._string_name = a.Named(syntax_element.STRING_SYNTAX_ELEMENT.singular_name)
        self._relativity_name = instruction_arguments.RELATIVITY_ARGUMENT

        self._tp = TextParser({
            'RELATIVITY_OPTION': self._relativity_name.name,
            'PATH_STRING': self._string_name.name,
            'posix_syntax': documentation_text.POSIX_SYNTAX,
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'path_type': formatting.keyword(types.PATH_TYPE_INFO.name.singular),
            'string_syntax_element': syntax_element.STRING_SYNTAX_ELEMENT.singular_name,
            'cd': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'SYMBOL_SYNTAX_ELEMENT_NAME': SYMBOL_SYNTAX_ELEMENT_NAME,
        })

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> list:
        return []

    def main_description_rest(self) -> list:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            syntax_element.STRING_SYNTAX_ELEMENT,
            concepts.SYMBOL_CONCEPT_INFO,
            types.LIST_TYPE_INFO,
        ])

    @staticmethod
    def _cl_arguments() -> list:
        return [
            a.Choice(a.Multiplicity.ZERO_OR_MORE,
                     [
                         syntax_element.STRING_SYNTAX_ELEMENT.argument,
                         instruction_arguments.SYMBOL_REFERENCE,
                     ]),
        ]


DOCUMENTATION = _Documentation()

_MAIN_DESCRIPTION_REST = """\
"""
