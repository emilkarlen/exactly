from typing import Sequence

from exactly_lib.definitions import instruction_arguments, matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.test_case_utils.expression import grammar, parser as parse_expression
from exactly_lib.test_case_utils.line_matcher.impl import matches_regex, line_number
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.type_system.logic.line_matcher import FIRST_LINE_NUMBER, LineMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

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


class ParserOfMatcherOnArbitraryLine(Parser[LineMatcherSdv]):
    def parse_from_token_parser(self, token_parser: TokenParser) -> LineMatcherSdv:
        return parse_line_matcher_from_token_parser(token_parser, must_be_on_current_line=False)


def parse_line_matcher_from_token_parser(parser: TokenParser,
                                         must_be_on_current_line: bool = True) -> LineMatcherSdv:
    return parse_expression.parse(GRAMMAR, parser,
                                  must_be_on_current_line=must_be_on_current_line)


ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS = {
    '_REG_EX_': REPLACE_REGEX_ARGUMENT.name,
    '_STRING_': REPLACE_REPLACEMENT_ARGUMENT.name,
}

_HELP_TEXT_TEMPLATE_FORMATS = ADDITIONAL_ERROR_MESSAGE_TEMPLATE_FORMATS.copy()

_HELP_TEXT_TEMPLATE_FORMATS.update({
    'FIRST_LINE_NUMBER': FIRST_LINE_NUMBER,
    'MODEL': matcher_model.LINE_MATCHER_MODEL,
})

_TP = TextParser(_HELP_TEXT_TEMPLATE_FORMATS)

_REGEX_MATCHER_SED_DESCRIPTION = """Matches {MODEL:s} that contains a given {_REG_EX_}."""

_LINE_NUMBER_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} with a given line number.


Line numbers start at {FIRST_LINE_NUMBER}.
"""


class _RegexSyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY,
                     REPLACE_REGEX_ARGUMENT),
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_REGEX_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target]


class _LineNumberSyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_LINE_NUMBER_MATCHER_SED_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target]


_CONCEPT = grammar.Concept(
    types.LINE_MATCHER_TYPE_INFO.name,
    types.LINE_MATCHER_TYPE_INFO.identifier,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.argument,
)

GRAMMAR = standard_expression_grammar.new_grammar(
    _CONCEPT,
    model=matcher_model.LINE_MATCHER_MODEL,
    value_type=ValueType.LINE_MATCHER,
    simple_expressions=(
        NameAndValue(
            line_matcher.REGEX_MATCHER_NAME,
            grammar.PrimitiveExpression(matches_regex.parse,
                                        _RegexSyntaxDescription())
        ),
        NameAndValue(
            line_matcher.LINE_NUMBER_MATCHER_NAME,
            grammar.PrimitiveExpression(line_number.parse_line_number,
                                        _LineNumberSyntaxDescription())
        ),
    ),
)
