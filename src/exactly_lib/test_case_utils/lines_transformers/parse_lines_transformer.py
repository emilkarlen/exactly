from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.types import LINES_TRANSFORMER_CONCEPT_INFO
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_parse
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.lines_transformers import custom_transformers as ct
from exactly_lib.test_case_utils.lines_transformers.resolvers import LinesTransformerConstant
from exactly_lib.test_case_utils.lines_transformers.transformers import IdentityLinesTransformer
from exactly_lib.test_case_utils.token_stream_parse_prime import TokenParserPrime
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.parse.token import TokenType
from exactly_lib.util.textformat.parse import normalize_and_parse

WITH_REPLACED_ENV_VARS_OPTION_NAME = a.OptionName(long_name='with-replaced-env-vars')
WITH_REPLACED_ENV_VARS_OPTION = option_syntax.option_syntax(WITH_REPLACED_ENV_VARS_OPTION_NAME)

REPLACE_TRANSFORMER_NAME = 'replace'

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(type_system.STRING_VALUE)


def parse_lines_transformer(source: ParseSource) -> LinesTransformerResolver:
    with_replaced_env_vars = False
    peek_source = source.copy
    next_arg = token_parse.parse_token_or_none_on_current_line(peek_source)
    if next_arg is not None and next_arg.type == TokenType.PLAIN and \
            matches(WITH_REPLACED_ENV_VARS_OPTION_NAME, next_arg.string):
        source.catch_up_with(peek_source)
        with_replaced_env_vars = True
    lines_transformer = IdentityLinesTransformer()
    if with_replaced_env_vars:
        lines_transformer = ct.CUSTOM_LINES_TRANSFORMERS[ct.ENV_VAR_REPLACEMENT_TRANSFORMER_NAME]
    return LinesTransformerConstant(lines_transformer)


def parse_replace(parser: TokenParserPrime) -> LinesTransformerResolver:
    raise NotImplementedError('todo')


def mk_lines_transformer_reference(symbol_name: str) -> LinesTransformerResolver:
    raise NotImplementedError('todo')


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
}


def _fnap(s: str) -> list:
    return normalize_and_parse(s.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS))


_REPLACE_TRANSFORMER_SED_DESCRIPTION = """\
Replaces the contents of a file.

All occurrences of {_REG_EX_} are replaced with {_STRING_}.
"""

_REPLACE_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REGEX_ARGUMENT),
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REPLACEMENT_ARGUMENT),
    ],
    description_rest=_fnap(_REPLACE_TRANSFORMER_SED_DESCRIPTION)
)

_CONCEPT = grammar.Concept(
    LINES_TRANSFORMER_CONCEPT_INFO.name,
    type_system.LINES_TRANSFORMER_TYPE,
    type_system.LINES_TRANSFORMER_VALUE,
)

_GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=mk_lines_transformer_reference,
    simple_expressions={
        REPLACE_TRANSFORMER_NAME:
            grammar.SimpleExpression(parse_replace,
                                     _REPLACE_SYNTAX_DESCRIPTION),
    },
    complex_expressions={},
    prefix_expressions={},
)
