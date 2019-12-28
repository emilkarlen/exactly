from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher, combinator_sdvs
from exactly_lib.test_case_utils.string_matcher.impl import line_matches
from exactly_lib.util.logic_types import ExpectationType, Quantifier


def parse(quantifier: Quantifier,
          expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    matcher = parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_line_matcher.ParserOfPlainMatcherOnArbitraryLine(),
        line_matches.ELEMENT_SETUP,
        token_parser
    )
    if expectation_type is ExpectationType.NEGATIVE:
        matcher = combinator_sdvs.Negation(matcher)

    return StringMatcherSdv(matcher)
