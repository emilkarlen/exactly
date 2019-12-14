from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters, property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.test_case_utils.string_matcher import matcher_options, sdvs
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherDdv
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

_ERR_MSG_MAX_NUM_LINES_TO_DISPLAY = 10


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherSdv:
    is_full_match = token_parser.consume_and_handle_optional_option(False,
                                                                    lambda parser: True,
                                                                    matcher_options.FULL_MATCH_ARGUMENT_OPTION)
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=False)

    return value_sdv(
        expectation_type,
        is_full_match,
        regex_sdv,
    )


def value_sdv(expectation_type: ExpectationType,
              is_full_match: bool,
              contents_matcher: RegexSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> StringMatcherDdv:
        regex_ddv = contents_matcher.resolve(symbols)
        regex_matcher = matches_regex.MatchesRegexDdv(expectation_type, regex_ddv, is_full_match)
        return property_matcher.PropertyMatcherDdv(
            regex_matcher,
            property_getters.PropertyGetterDdvConstant(
                _PropertyGetter(),
            ),
            property_matcher_describers.IdenticalToMatcher(),
        )

    return sdvs.string_matcher_sdv_from_parts_2(contents_matcher.references, get_ddv)


class _PropertyGetter(PropertyGetter[FileToCheck, str]):
    def get_from(self, model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(lines)
