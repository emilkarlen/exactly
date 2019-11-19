from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcherDdv
from exactly_lib.test_case_utils.string_matcher.sdvs import StringMatcherSdvConstantOfDdv
from exactly_lib.util.logic_types import ExpectationType


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    return value_sdv(expectation_type)


def value_sdv(expectation_type: ExpectationType) -> StringMatcherSdv:
    return StringMatcherSdvConstantOfDdv(
        EmptinessStringMatcherDdv(expectation_type)
    )
