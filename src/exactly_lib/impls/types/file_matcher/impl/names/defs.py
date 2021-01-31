from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import str_matcher
from exactly_lib.util.cli_syntax.elements import argument as a

REG_EX_OPERATOR = a.Named(str_matcher.MATCH_REGEX_ARGUMENT__SHORT)

GLOB_OR_REGEX__ARG_USAGE = a.Choice.of_multiple_argument_choices(
    a.Multiplicity.MANDATORY,
    [
        [syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument],
        [REG_EX_OPERATOR, syntax_elements.REGEX_SYNTAX_ELEMENT.argument],
    ])
