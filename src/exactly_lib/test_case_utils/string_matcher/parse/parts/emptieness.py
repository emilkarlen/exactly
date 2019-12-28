from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher.impls import combinator_sdvs
from exactly_lib.test_case_utils.string_matcher.impl import emptiness
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return StringMatcherSdv(
        combinator_sdvs.of_expectation_type(
            parse__generic(token_parser),
            expectation_type
        ),
    )


def parse__generic(token_parser: TokenParser) -> MatcherSdv[FileToCheck]:
    return emptiness.sdv__generic()
