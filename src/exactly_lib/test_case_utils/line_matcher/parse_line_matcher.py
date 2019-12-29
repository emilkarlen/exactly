from typing import Sequence

from exactly_lib.definitions import expression, instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.line_matcher.impl import matches_regex, line_number
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs, sdv_components, constant
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.type_system.logic.line_matcher import FIRST_LINE_NUMBER, LineMatcherLine, LineMatcherSdvType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

CONSTANT_TRUE_MATCHER_SDV = LineMatcherSdv(
    sdv_components.matcher_sdv_from_constant_primitive(constant.MatcherWithConstantResult(True))
)

REPLACE_REGEX_ARGUMENT = instruction_arguments.REG_EX

REPLACE_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)

_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + REPLACE_REPLACEMENT_ARGUMENT.name

LINE_MATCHER_ARGUMENT = a.Named(types.LINE_MATCHER_TYPE_INFO.syntax_element_name)


def parser() -> Parser[LineMatcherSdv]:
    return _PARSER


class _Parser(Parser[LineMatcherSdv]):
    def parse_from_token_parser(self, parser: TokenParser) -> LineMatcherSdv:
        return parse_line_matcher_from_token_parser(parser)


_PARSER = _Parser()


class ParserOfGenericMatcherOnArbitraryLine(Parser[MatcherSdv[LineMatcherLine]]):
    def parse_from_token_parser(self, token_parser: TokenParser) -> MatcherSdv[LineMatcherLine]:
        return parse_line_matcher_from_token_parser__generic(token_parser, must_be_on_current_line=False)


def parse_line_matcher_from_token_parser(parser: TokenParser,
                                         must_be_on_current_line: bool = True) -> LineMatcherSdv:
    return LineMatcherSdv(
        parse_line_matcher_from_token_parser__generic(parser, must_be_on_current_line)
    )


def parse_line_matcher_from_token_parser__generic(parser: TokenParser,
                                                  must_be_on_current_line: bool = True) -> LineMatcherSdvType:
    return parse_expression.parse(GRAMMAR, parser,
                                  must_be_on_current_line=must_be_on_current_line)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
}

_HELP_TEXT_TEMPLATE_FORMATS = ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS.copy()

_HELP_TEXT_TEMPLATE_FORMATS.update({
    'FIRST_LINE_NUMBER': FIRST_LINE_NUMBER,
})

_TP = TextParser(_HELP_TEXT_TEMPLATE_FORMATS)

_REGEX_MATCHER_SED_DESCRIPTION = """Matches lines that contains a given {_REG_EX_}."""

_LINE_NUMBER_MATCHER_SED_DESCRIPTION = """\
Matches lines with a given line number.


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
    description_rest=_TP.fnap(_REGEX_MATCHER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target],
)

_LINE_NUMBER_SYNTAX_DESCRIPTION = grammar.SimpleExpressionDescription(
    argument_usage_list=[
        syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
    ],
    description_rest=_TP.fnap(_LINE_NUMBER_MATCHER_SED_DESCRIPTION),
    see_also_targets=[syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target],
)

_CONCEPT = grammar.Concept(
    types.LINE_MATCHER_TYPE_INFO.name,
    types.LINE_MATCHER_TYPE_INFO.identifier,
    LINE_MATCHER_ARGUMENT,
)


def _mk_reference(name: str) -> LineMatcherSdvType:
    return MatcherReferenceSdv(name, ValueType.LINE_MATCHER)


def _mk_negation(operand: LineMatcherSdvType) -> LineMatcherSdvType:
    return combinator_sdvs.Negation(operand)


def _mk_conjunction(operands: Sequence[LineMatcherSdvType]) -> LineMatcherSdvType:
    return combinator_sdvs.Conjunction(operands)


def _mk_disjunction(operands: Sequence[LineMatcherSdvType]) -> LineMatcherSdvType:
    return combinator_sdvs.Disjunction(operands)


GRAMMAR = grammar.Grammar(
    _CONCEPT,
    mk_reference=_mk_reference,
    simple_expressions={
        line_matcher.REGEX_MATCHER_NAME:
            grammar.SimpleExpression(matches_regex.parse__generic,
                                     _REGEX_SYNTAX_DESCRIPTION),
        line_matcher.LINE_NUMBER_MATCHER_NAME:
            grammar.SimpleExpression(line_number.parse_line_number__generic,
                                     _LINE_NUMBER_SYNTAX_DESCRIPTION),
    },
    complex_expressions={
        expression.AND_OPERATOR_NAME:
            grammar.ComplexExpression(_mk_conjunction,
                                      grammar.OperatorExpressionDescription(
                                          _TP.fnap(_AND_SED_DESCRIPTION)
                                      )),
        expression.OR_OPERATOR_NAME:
            grammar.ComplexExpression(_mk_disjunction,
                                      grammar.OperatorExpressionDescription(
                                          _TP.fnap(_OR_SED_DESCRIPTION)
                                      )),
    },
    prefix_expressions={
        expression.NOT_OPERATOR_NAME:
            grammar.PrefixExpression(_mk_negation,
                                     grammar.OperatorExpressionDescription(
                                         _TP.fnap(_NOT_SED_DESCRIPTION)
                                     ))
    },
)
