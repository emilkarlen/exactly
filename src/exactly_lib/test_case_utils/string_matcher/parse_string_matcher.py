from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.impl import on_transformed
from exactly_lib.test_case_utils.string_matcher.parse.parts import emptieness, equality, line_matches, matches, \
    num_lines, run_program
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def string_matcher_parser() -> Parser[StringMatcherSdv]:
    return parsers.ParserFromTokenParserFunction(parse_string_matcher,
                                                 consume_last_line_if_is_at_eol_after_parse=False)


def parse_string_matcher(parser: TokenParser,
                         must_be_on_current_line: bool = False) -> StringMatcherSdv:
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _parse_on_transformed(parser: TokenParser) -> StringMatcherSdv:
    transformer = parse_string_transformer.parse_string_transformer_from_token_parser(parser,
                                                                                      must_be_on_current_line=False)
    matcher_on_transformed = parse_string_matcher(parser,
                                                  must_be_on_current_line=False)
    return on_transformed.StringMatcherWithTransformationSdv(transformer, matcher_on_transformed)


class _OnTransformedDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return TextParser().fnap(_DESCRIPTION__ON_TRANSFORMED)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.cross_reference_target,


def _simple_expressions() -> Sequence[NameAndValue[grammar.PrimitiveExpression[StringMatcherSdv]]]:
    ret_val = [
        NameAndValue(
            matcher_options.EMPTY_ARGUMENT,
            grammar.PrimitiveExpression(emptieness.parse,
                                        emptieness.Description())
        ),
        NameAndValue(
            matcher_options.EQUALS_ARGUMENT,
            grammar.PrimitiveExpression(equality.parse,
                                        equality.Description())
        ),
        NameAndValue(
            matcher_options.MATCHES_ARGUMENT,
            grammar.PrimitiveExpression(matches.parse,
                                        matches.Description())
        ),
    ]

    quantification_setup = parse_quantified_matcher.GrammarSetup(
        line_matches.line_matchers.ELEMENT_SETUP,
        parse_line_matcher.ParserOfMatcherOnArbitraryLine(),
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            matcher_options.NUM_LINES_ARGUMENT,
            grammar.PrimitiveExpression(num_lines.parse,
                                        num_lines.Description())
        ),
        NameAndValue(
            option_syntax.option_syntax(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            grammar.PrimitiveExpression(_parse_on_transformed,
                                        _OnTransformedDescription())
        ),
        NameAndValue(
            matcher_options.RUN_PROGRAM_ARGUMENT,
            grammar.PrimitiveExpression(
                run_program.parse,
                run_program.SyntaxDescription(),
            )
        ),
    ]

    return ret_val


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.STRING_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.STRING_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.STRING_MATCHER_MODEL,
    value_type=ValueType.STRING_MATCHER,
    simple_expressions=_simple_expressions(),
)

_DESCRIPTION__ON_TRANSFORMED = """\
Applies a matcher to a transformed variant of the string.
"""
