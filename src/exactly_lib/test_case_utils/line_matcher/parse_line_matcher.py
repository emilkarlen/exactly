from exactly_lib.help_texts import expression
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.resolver_structure import LineMatcherResolver
from exactly_lib.test_case_utils.condition.integer.parse_integer_condition import parse_integer_matcher
from exactly_lib.test_case_utils.condition.syntax import OPERATOR_ARGUMENT
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.line_matcher import line_matchers
from exactly_lib.test_case_utils.line_matcher import resolvers
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.type_system.logic.line_matcher import FIRST_LINE_NUMBER
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.parse import normalize_and_parse

CONSTANT_TRUE_MATCHER_RESOLVER = resolvers.LineMatcherConstantResolver(line_matchers.LineMatcherConstant(True))

REGEX_MATCHER_NAME = 'regex'

LINE_NUMBER_MATCHER_NAME = 'line-num'

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)

_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

LINE_MATCHER_ARGUMENT = a.Named(types.LINE_MATCHER_TYPE_INFO.syntax_element_name)

LINE_NUMBER_PROPERTY = 'line number'


def parse_line_matcher(source: ParseSource) -> LineMatcherResolver:
    with token_stream_parser.from_parse_source(source) as tp:
        return parse_optional_matcher_resolver(tp)


def parse_optional_matcher_resolver(parser: TokenParser) -> LineMatcherResolver:
    return parser.consume_and_handle_optional_option(
        CONSTANT_TRUE_MATCHER_RESOLVER,
        parse_line_matcher_from_token_parser,
        WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def parse_line_matcher_from_token_parser(parser: TokenParser) -> LineMatcherResolver:
    return parse_expression.parse(GRAMMAR, parser)


def parse_regex(parser: TokenParser) -> LineMatcherResolver:
    regex = parse_reg_ex.parse_regex(parser)
    return resolvers.LineMatcherConstantResolver(line_matchers.LineMatcherRegex(regex))


def parse_line_number(parser: TokenParser) -> LineMatcherResolver:
    integer_matcher = parse_integer_matcher(parser,
                                            name_of_lhs=LINE_NUMBER_PROPERTY)
    return resolvers.LineMatcherConstantResolver(line_matchers.LineMatcherLineNumber(integer_matcher))


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
}

_HELP_TEXT_TEMPLATE_FORMATS = ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS.copy()

_HELP_TEXT_TEMPLATE_FORMATS.update({
    'FIRST_LINE_NUMBER': FIRST_LINE_NUMBER,
    'INTEGER_COMPARISON': syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.argument.name,
})


def _fnap(s: str) -> list:
    return normalize_and_parse(s.format_map(_HELP_TEXT_TEMPLATE_FORMATS))


_REGEX_MATCHER_SED_DESCRIPTION = """Matches lines that contains a given {_REG_EX_}."""

_LINE_NUMBER_MATCHER_SED_DESCRIPTION = """\
Matches lines with a given line number.


Comparision is that of {INTEGER_COMPARISON}, except that symbol references are not substituted.


Line numbers start at {FIRST_LINE_NUMBER}.
"""

_NOT_SED_DESCRIPTION = """\
Matches lines not matched by the given matcher.
"""

_AND_SED_DESCRIPTION = """\
Matches lines matched by all matchers.
"""

_OR_SED_DESCRIPTION = """\
Matches lines matched by any matcher.
"""

_REGEX_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 REPLACE_REGEX_ARGUMENT),
    ],
    description_rest=_fnap(_REGEX_MATCHER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target],
)

_LINE_NUMBER_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        a.Single(a.Multiplicity.MANDATORY,
                 OPERATOR_ARGUMENT),
        a.Single(a.Multiplicity.MANDATORY,
                 a.Named('INT')),
    ],
    description_rest=_fnap(_LINE_NUMBER_MATCHER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.cross_reference_target],
)

_CONCEPT = grammar.Concept(
    types.LINE_MATCHER_TYPE_INFO.name,
    types.LINE_MATCHER_TYPE_INFO.identifier,
    LINE_MATCHER_ARGUMENT,
)

GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=resolvers.LineMatcherReferenceResolver,
    simple_expressions={
        REGEX_MATCHER_NAME:
            grammar.SimpleExpression(parse_regex,
                                     _REGEX_SYNTAX_DESCRIPTION),
        LINE_NUMBER_MATCHER_NAME:
            grammar.SimpleExpression(parse_line_number,
                                     _LINE_NUMBER_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        expression.AND_OPERATOR_NAME:
            grammar.ComplexExpression(resolvers.LineMatcherAndResolver,
                                      grammar.OperatorExpressionDescription(
                                          _fnap(_AND_SED_DESCRIPTION)
                                      )),
        expression.OR_OPERATOR_NAME:
            grammar.ComplexExpression(resolvers.LineMatcherOrResolver,
                                      grammar.OperatorExpressionDescription(
                                          _fnap(_OR_SED_DESCRIPTION)
                                      )),
    },
    prefix_expressions={
        expression.NOT_OPERATOR_NAME:
            grammar.PrefixExpression(resolvers.LineMatcherNotResolver,
                                     grammar.OperatorExpressionDescription(
                                         _fnap(_NOT_SED_DESCRIPTION)
                                     ))
    },
)
