from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.test_case_utils.string_matcher.impl import line_matchers
from exactly_lib.type_system.logic.string_matcher import StringMatcherSdv
from exactly_lib.util.logic_types import Quantifier


def parse(quantifier: Quantifier,
          token_parser: TokenParser) -> StringMatcherSdv:
    return parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_line_matcher.ParserOfMatcherOnArbitraryLine(),
        line_matchers.ELEMENT_SETUP,
        token_parser
    )


def parse__all(parser: TokenParser) -> StringMatcherSdv:
    return parse(Quantifier.ALL, parser)


def parse__exists(parser: TokenParser) -> StringMatcherSdv:
    return parse(Quantifier.EXISTS, parser)
