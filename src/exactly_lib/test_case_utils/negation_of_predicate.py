from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts.instruction_arguments import NEGATION_ARGUMENT_STR
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse


def syntax_element_description(additional_text: str = '') -> SyntaxElementDescription:
    return SyntaxElementDescription(NEGATION_ARGUMENT_STR,
                                    normalize_and_parse(_ASSERTION_NEGATION_ELEMENT_DESCRIPTION + additional_text))


def optional_negation_argument_usage() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.OPTIONAL,
                    a.Constant(NEGATION_ARGUMENT_STR))


_ASSERTION_NEGATION_ELEMENT_DESCRIPTION = """\
Negates the assertion.
"""
