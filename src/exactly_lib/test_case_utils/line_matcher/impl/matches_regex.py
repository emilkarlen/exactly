from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters, property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.logic_types import ExpectationType


def parse(token_parser: TokenParser) -> LineMatcherSdv:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=True)

    return _sdv(regex_sdv)


def _sdv(regex: RegexSdv) -> LineMatcherSdv:
    matcher_sdv = property_matcher.PropertyMatcherSdv(
        matches_regex.MatchesRegexSdv(ExpectationType.POSITIVE, regex, False),
        property_getters.sdv_of_constant_primitive(
            _PropertyGetter(),
        ),
        property_matcher_describers.IdenticalToMatcher(),
    )
    return LineMatcherSdv(matcher_sdv)


class _PropertyGetter(PropertyGetter[LineMatcherLine, str]):
    def get_from(self, model: LineMatcherLine) -> str:
        return model[1]
