from typing import Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver
from exactly_lib.test_case_utils.string_matcher import matcher_options, resolvers
from exactly_lib.test_case_utils.string_matcher.delegated_matcher import StringMatcherValueDelegatedToMatcher
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherValue
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

_ERR_MSG_MAX_NUM_LINES_TO_DISPLAY = 10


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> StringMatcherResolver:
    is_full_match = token_parser.consume_and_handle_optional_option(False,
                                                                    lambda parser: True,
                                                                    matcher_options.FULL_MATCH_ARGUMENT_OPTION)
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_resolver = parse_regex.parse_regex2(token_parser,
                                                           must_be_on_same_line=False)

    return value_resolver(
        expectation_type,
        is_full_match,
        regex_resolver,
    )


def value_resolver(expectation_type: ExpectationType,
                   is_full_match: bool,
                   contents_matcher: RegexResolver) -> StringMatcherResolver:
    def get_value_validator(symbols: SymbolTable) -> PreOrPostSdsValueValidator:
        return contents_matcher.resolve(symbols).validator()

    def get_value(symbols: SymbolTable) -> StringMatcherValue:
        regex_value = contents_matcher.resolve(symbols)
        regex_matcher = matches_regex.MatchesRegexValue(expectation_type, regex_value, is_full_match, )
        return StringMatcherValueDelegatedToMatcher(
            property_matcher.PropertyMatcherValue(
                regex_matcher,
                property_getters.PropertyGetterValueConstant(
                    _PropertyGetter(),
                ),
            ),
        )

    return resolvers.StringMatcherResolverFromParts2(
        contents_matcher.references,
        pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(get_value_validator),
        get_value,
    )


class _PropertyGetter(PropertyGetter[FileToCheck, str]):
    @property
    def name(self) -> Optional[str]:
        return None

    def get_from(self, model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(lines)
