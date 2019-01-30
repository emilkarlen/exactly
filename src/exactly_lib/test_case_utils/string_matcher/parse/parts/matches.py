from typing import Optional, Pattern, Match

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.error_messages import ExpectedValueResolver, ErrorMessageResolverConstructor
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromValueWithValidation, \
    StringMatcherValueWithValidation
from exactly_lib.type_system.error_message import ErrorMessageResolver, \
    ConstantErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


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
    error_message_constructor = ErrorMessageResolverConstructor(expectation_type,
                                                                ExpectedValueResolver(matcher_options.MATCHES_ARGUMENT,
                                                                                      contents_matcher))

    def get_value_with_validator(symbols: SymbolTable) -> StringMatcherValueWithValidation:
        regex_value = contents_matcher.resolve(symbols)

        def get_matcher(tcds: HomeAndSds) -> StringMatcher:
            return MatchesRegexStringMatcher(
                expectation_type,
                is_full_match,
                regex_value.value_of_any_dependency(tcds),
                error_message_constructor,
            )

        return StringMatcherValueWithValidation(
            regex_value.resolving_dependencies(),
            regex_value.validator(),
            get_matcher,
        )

    return StringMatcherResolverFromValueWithValidation(
        contents_matcher.references,
        get_value_with_validator,
    )


class MatchesRegexStringMatcher(StringMatcher):
    def __init__(self,
                 expectation_type: ExpectationType,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 error_message_constructor: ErrorMessageResolverConstructor,
                 ):
        self._expectation_type = expectation_type
        self._is_full_match = is_full_match
        self._pattern = pattern
        self._err_msg_constructor = error_message_constructor

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        actual_contents = self._actual_contents(model)
        match = self._find_match(actual_contents)
        if match is None:
            if self._expectation_type is ExpectationType.POSITIVE:
                return ConstantErrorMessageResolver('Not found: ' + self._pattern.pattern)
            else:
                return None
        else:
            if self._expectation_type is ExpectationType.POSITIVE:
                return None
            else:
                return ConstantErrorMessageResolver('Found: ' + self._pattern.pattern)

    def _find_match(self, actual_contents: str) -> Match:
        if self._is_full_match:
            return self._pattern.fullmatch(actual_contents)
        else:
            return self._pattern.search(actual_contents)

    def _actual_contents(self, model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(lines)

    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self._expectation_type) + matcher_options.MATCHES_ARGUMENT
