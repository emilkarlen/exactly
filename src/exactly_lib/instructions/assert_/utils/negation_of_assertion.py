from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse

NEGATION_ARGUMENT_STR = '!'


def syntax_element_description() -> SyntaxElementDescription:
    return SyntaxElementDescription(NEGATION_ARGUMENT_STR,
                                    normalize_and_parse(_NEGATION_ELEMENT_DESCRIPTION))


def optional_negation_argument_usage() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.OPTIONAL,
                    a.Constant(NEGATION_ARGUMENT_STR))


_NEGATION_ELEMENT_DESCRIPTION = """\
Negates the assertion.
"""
