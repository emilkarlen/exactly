from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher
from exactly_lib.test_case_utils.string_matcher.impl import num_lines
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    matcher = parse_integer_matcher.parse(
        token_parser,
        expectation_type,
        parse_integer_matcher.validator_for_non_negative,
    )
    return num_lines.sdv(matcher)
