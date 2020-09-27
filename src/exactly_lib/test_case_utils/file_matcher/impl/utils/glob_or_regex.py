from typing import Callable

from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers import token_stream_parsing
from exactly_lib.section_document.element_parsers.token_stream_parser import ParserFromTokens, TokenParser
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse import token_matchers

REG_EX_OPERATOR = a.Named('~')

GLOB_OR_REGEX__ARG_USAGE = a.Choice.of_multiple_argument_choices(
    a.Multiplicity.MANDATORY,
    [
        [syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument],
        [REG_EX_OPERATOR, syntax_elements.REGEX_SYNTAX_ELEMENT.argument],
    ])


def parser(
        glob_variant_parser: Callable[[TokenParser], FileMatcherSdv],
        regex_variant_parser: Callable[[TokenParser], FileMatcherSdv],
) -> ParserFromTokens[FileMatcherSdv]:
    return token_stream_parsing.ParserWithDefault(
        _SYNTAX_ELEM_STR,
        [
            token_stream_parsing.TokenSyntaxSetup(
                token_matchers.is_unquoted_and_equals(REG_EX_OPERATOR.name),
                regex_variant_parser,
            ),
        ],
        glob_variant_parser,
    )


_SYNTAX_ELEM_STR = cl_syntax.cl_syntax_for_args((GLOB_OR_REGEX__ARG_USAGE,))
