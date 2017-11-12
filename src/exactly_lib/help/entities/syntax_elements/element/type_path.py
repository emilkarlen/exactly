from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.help_texts.entity.syntax_element import STRING_SYNTAX_ELEMENT
from exactly_lib.util.cli_syntax.elements import argument as a


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(syntax_element.PATH_SYNTAX_ELEMENT)

        self._parser = TextParser()

        self._string_name = a.Named(STRING_SYNTAX_ELEMENT.singular_name)
        self._relativity_name = instruction_arguments.RELATIVITY_ARGUMENT

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            self._relativity_sed(),
            self._string_sed(),
        ]

    def main_description_rest(self) -> list:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def see_also_targets(self) -> list:
        return [
            STRING_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _relativity_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._relativity_name.name,
                                        self._parser.fnap(_RELATIVITY_DESCRIPTION_REST))

    def _string_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._string_name.name,
                                        self._parser.fnap(_STRING_DESCRIPTION_REST))

    def _cl_arguments(self) -> list:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     self._relativity_name),
            a.Single(a.Multiplicity.MANDATORY,
                     self._string_name),

        ]


DOCUMENTATION = _Documentation()

_MAIN_DESCRIPTION_REST = """\
Main description rest
"""

_STRING_DESCRIPTION_REST = """\
String description rest
"""

_RELATIVITY_DESCRIPTION_REST = """\
Relativity description rest
"""
