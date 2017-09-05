from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity.types import LINE_MATCHER_CONCEPT_INFO
from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.named_element.resolver_structure import LineMatcherResolver
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression, syntax_documentation
from exactly_lib.test_case_utils.line_matcher import line_matchers
from exactly_lib.test_case_utils.line_matcher import resolvers
from exactly_lib.test_case_utils.parse.reg_ex import compile_regex
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs

CONSTANT_TRUE_MATCHER_RESOLVER = resolvers.LineMatcherConstantResolver(line_matchers.LineMatcherConstant(True))

REGEX_MATCHER_NAME = 'regex'

AND_OPERATOR_NAME = '&&'

OR_OPERATOR_NAME = '||'

NOT_OPERATOR_NAME = '!'

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(type_system.STRING_VALUE)

_MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REGEX_ARGUMENT.name

_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

LINE_MATCHER_ARGUMENT = a.Named(type_system.LINE_MATCHER_VALUE)


def selection_syntax_element_description() -> SyntaxElementDescription:
    return cl_syntax.cli_argument_syntax_element_description(
        instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
        docs.paras(_TRANSFORMATION_DESCRIPTION),
        [
            InvokationVariant(cl_syntax.arg_syntax(instruction_arguments.TRANSFORMATION_OPTION)),
        ]
    )


def transformer_syntax_element_description() -> SyntaxElementDescription:
    return syntax_documentation.Syntax(GRAMMAR).syntax_element_description()


_TRANSFORMATION_DESCRIPTION = """\
Transforms the contents of the tested file before it is tested.
"""


def parse_line_matcher(source: ParseSource) -> LineMatcherResolver:
    with token_stream_parse_prime.from_parse_source(source) as tp:
        return parse_optional_matcher_resolver(tp)


def parse_optional_matcher_resolver(parser: TokenParserPrime) -> LineMatcherResolver:
    return parser.consume_and_handle_optional_option(
        CONSTANT_TRUE_MATCHER_RESOLVER,
        parse_line_matcher_from_token_parser,
        WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_line_matcher_from_token_parser(parser: TokenParserPrime) -> LineMatcherResolver:
    return parse_expression.parse(GRAMMAR, parser)


def parse_regex(parser: TokenParserPrime) -> LineMatcherResolver:
    parser.require_is_not_at_eol(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    regex_pattern = parser.consume_mandatory_token(_MISSING_REGEX_ARGUMENT_ERR_MSG)
    regex = compile_regex(regex_pattern.string)
    return resolvers.LineMatcherConstantResolver(line_matchers.LineMatcherRegex(regex))


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
}


def _fnap(s: str) -> list:
    return normalize_and_parse(s.format_map(ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS))


_REGEX_MATCHER_SED_DESCRIPTION = """Matches lines that contains a given {_REG_EX_}."""

_NOT_TRANSFORMER_SED_DESCRIPTION = """\
Matches lines NOT matched by the given matcher.
"""

_AND_TRANSFORMER_SED_DESCRIPTION = """\
Matches lines matched by all matchers.
"""

_OR_TRANSFORMER_SED_DESCRIPTION = """\
Matches lines matched by any matcher.
"""

_REGEX_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REGEX_ARGUMENT),
    ],
    description_rest=_fnap(_REGEX_MATCHER_SED_DESCRIPTION)
)

_AND_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _fnap(_AND_TRANSFORMER_SED_DESCRIPTION)
)

_OR_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _fnap(_OR_TRANSFORMER_SED_DESCRIPTION)
)

_NOT_SYNTAX_DESCRIPTION = grammar.OperatorExpressionDescription(
    _fnap(_NOT_TRANSFORMER_SED_DESCRIPTION)
)

_CONCEPT = grammar.Concept(
    LINE_MATCHER_CONCEPT_INFO.name,
    type_system.LINE_MATCHER_TYPE,
    LINE_MATCHER_ARGUMENT,
)

GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=resolvers.LineMatcherReferenceResolver,
    simple_expressions={
        REGEX_MATCHER_NAME:
            grammar.SimpleExpression(parse_regex,
                                     _REGEX_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        AND_OPERATOR_NAME: grammar.ComplexExpression(
            resolvers.LineMatcherAndResolver,
            _AND_SYNTAX_DESCRIPTION,
        ),
        OR_OPERATOR_NAME: grammar.ComplexExpression(
            resolvers.LineMatcherOrResolver,
            _OR_SYNTAX_DESCRIPTION,
        ),
    },
    prefix_expressions={
        NOT_OPERATOR_NAME: grammar.PrefixExpression(resolvers.LineMatcherNotResolver,
                                                    _NOT_SYNTAX_DESCRIPTION)
    },
)
