from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.impl import on_transformed
from exactly_lib.test_case_utils.string_matcher.parse.parts import emptieness
from exactly_lib.test_case_utils.string_matcher.parse.parts import equality
from exactly_lib.test_case_utils.string_matcher.parse.parts import line_matches
from exactly_lib.test_case_utils.string_matcher.parse.parts import matches
from exactly_lib.test_case_utils.string_matcher.parse.parts import num_lines
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.string_matcher import GenericStringMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def string_matcher_parser() -> Parser[StringMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_string_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=True)


def parse_string_matcher(parser: TokenParser,
                         must_be_on_current_line: bool = False) -> StringMatcherSdv:
    return StringMatcherSdv(parse_string_matcher__generic(parser, must_be_on_current_line))


def parse_string_matcher__generic(parser: TokenParser,
                                  must_be_on_current_line: bool = True) -> GenericStringMatcherSdv:
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _parse_on_transformed__generic(parser: TokenParser) -> GenericStringMatcherSdv:
    transformer = parse_string_transformer.parse_string_transformer_from_token_parser(parser,
                                                                                      must_be_on_current_line=False)
    matcher_on_transformed = parse_string_matcher__generic(parser,
                                                           must_be_on_current_line=False)
    return on_transformed.StringMatcherWithTransformationSdv(transformer, matcher_on_transformed)


class _OnTransformedDescription(grammar.SimpleExpressionDescription):
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


def _simple_expressions() -> Sequence[NameAndValue[grammar.SimpleExpression[GenericStringMatcherSdv]]]:
    ret_val = [
        NameAndValue(
            matcher_options.EMPTY_ARGUMENT,
            grammar.SimpleExpression(emptieness.parse__generic,
                                     emptieness.Description())
        ),
        NameAndValue(
            matcher_options.EQUALS_ARGUMENT,
            grammar.SimpleExpression(equality.parse__generic,
                                     equality.Description())
        ),
        NameAndValue(
            matcher_options.MATCHES_ARGUMENT,
            grammar.SimpleExpression(matches.parse__generic,
                                     matches.Description())
        ),
    ]

    quantification_setup = parse_quantified_matcher.GrammarSetup(
        line_matches.line_matches.ELEMENT_SETUP,
        parse_line_matcher.ParserOfGenericMatcherOnArbitraryLine(),
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            matcher_options.NUM_LINES_ARGUMENT,
            grammar.SimpleExpression(num_lines.parse__generic,
                                     num_lines.Description())
        ),
        NameAndValue(
            option_syntax.option_syntax(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            grammar.SimpleExpression(_parse_on_transformed__generic,
                                     _OnTransformedDescription())
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
