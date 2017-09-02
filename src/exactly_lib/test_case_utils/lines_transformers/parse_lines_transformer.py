from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity.types import LINES_TRANSFORMER_CONCEPT_INFO
from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression, syntax_documentation
from exactly_lib.test_case_utils.lines_transformers import resolvers
from exactly_lib.test_case_utils.lines_transformers.transformers import IdentityLinesTransformer, \
    ReplaceLinesTransformer
from exactly_lib.test_case_utils.parse.reg_ex import compile_regex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

IDENTITY_TRANSFORMER_RESOLVER = resolvers.LinesTransformerConstant(IdentityLinesTransformer())

REPLACE_TRANSFORMER_NAME = 'replace'

SEQUENCE_OPERATOR_NAME = '|'

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(type_system.STRING_VALUE)

_MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REGEX_ARGUMENT.name

_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

LINES_TRANSFORMER_ARGUMENT = a.Named(type_system.LINES_TRANSFORMER_VALUE)


def selection_syntax_element_description() -> SyntaxElementDescription:
    return cl_syntax.cli_argument_syntax_element_description(
        instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
        docs.paras(_TRANSFORMATION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(instruction_arguments.TRANSFORMATION_OPTION)),
        ]
    )


def selector_syntax_element_description() -> SyntaxElementDescription:
    return syntax_documentation.Syntax(_GRAMMAR).syntax_element_description()


_TRANSFORMATION_DESCRIPTION = """\
Transforms the contents of the tested file before it is tested.
"""


def parse_lines_transformer(source: ParseSource) -> LinesTransformerResolver:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse_optional_transformer_resolver(tp)


def parse_optional_transformer_resolver(parser: TokenParserPrime) -> LinesTransformerResolver:
    return parser.consume_and_handle_optional_option(
        IDENTITY_TRANSFORMER_RESOLVER,
        parse_lines_transformer_from_token_parser,
        WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_lines_transformer_from_token_parser(parser: TokenParserPrime) -> LinesTransformerResolver:
    return parse_expression.parse(_GRAMMAR, parser)


def parse_replace(parser: TokenParserPrime) -> LinesTransformerResolver:
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    regex_pattern = parser.consume_mandatory_token(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    parser.require_is_not_at_eol(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    replacement = parser.consume_mandatory_token(_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG)
    regex = compile_regex(regex_pattern.string)
    return resolvers.LinesTransformerConstant(ReplaceLinesTransformer(regex, replacement.string))


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
    '_TRANSFORMER_': LINES_TRANSFORMER_CONCEPT_INFO.name.singular,
    '_TRANSFORMERS_': LINES_TRANSFORMER_CONCEPT_INFO.name.plural,
}


def _fnap(s: str) -> list:
    return normalize_and_parse(s.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS))


_REPLACE_TRANSFORMER_SED_DESCRIPTION = """\
Replaces the contents of a file.

All occurrences of {_REG_EX_} are replaced with {_STRING_}.
"""

_SEQUENCE_TRANSFORMER_SED_DESCRIPTION = """\
Sequence of two or more {_TRANSFORMERS_}.

The result of the {_TRANSFORMER_} to the left is feed to the
{_TRANSFORMER_} to the right.
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

_SEQUENCE_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _fnap(_SEQUENCE_TRANSFORMER_SED_DESCRIPTION)
)

_CONCEPT = grammar.Concept(
    LINES_TRANSFORMER_CONCEPT_INFO.name,
    type_system.LINES_TRANSFORMER_TYPE,
    LINES_TRANSFORMER_ARGUMENT,
)

_GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=resolvers.LinesTransformerReference,
    simple_expressions={
        REPLACE_TRANSFORMER_NAME:
            grammar.SimpleExpression(parse_replace,
                                     _REPLACE_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        SEQUENCE_OPERATOR_NAME: grammar.ComplexExpression(
            resolvers.LinesTransformerSequenceResolver,
            _SEQUENCE_SYNTAX_DESCRIPTION,
        ),
    },
    prefix_expressions={},
)
