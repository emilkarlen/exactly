from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.definitions import logic
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse


def assertion_syntax_element_description(additional_text: str = '') -> SyntaxElementDescription:
    return SyntaxElementDescription(logic.NOT_OPERATOR_NAME,
                                    normalize_and_parse(_ASSERTION_NEGATION_ELEMENT_DESCRIPTION + additional_text))


def matcher_syntax_element_description(additional_text: str = '') -> SyntaxElementDescription:
    return SyntaxElementDescription(logic.NOT_OPERATOR_NAME,
                                    normalize_and_parse(_MATCHER_NEGATION_ELEMENT_DESCRIPTION + additional_text))


def optional_negation_argument_usage() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.OPTIONAL,
                    a.Constant(logic.NOT_OPERATOR_NAME))


_ASSERTION_NEGATION_ELEMENT_DESCRIPTION = """\
Negates the assertion.
"""

_MATCHER_NEGATION_ELEMENT_DESCRIPTION = """\
Negates the matcher.
"""
