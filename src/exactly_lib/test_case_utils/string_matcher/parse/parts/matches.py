import difflib
import pathlib
from typing import List, Optional, Pattern, Match

from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.program.string_or_file import SourceType
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.err_msg import diff_msg, diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromValueWithValidation, \
    StringMatcherValueWithValidation
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor, ErrorMessageResolver, \
    ErrorMessageResolvingEnvironment, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher
from exactly_lib.util import file_utils
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
    if source_type is not SourceType.HERE_DOC:
        token_parser.report_superfluous_arguments_if_not_at_eol()
        token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

    return value_resolver(
        expectation_type,
        is_full_match,
        regex_resolver,
    )


def value_resolver(expectation_type: ExpectationType,
                   is_full_match: bool,
                   contents_matcher: RegexResolver) -> StringMatcherResolver:
    error_message_constructor = _ErrorMessageResolverConstructor(expectation_type,
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


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self,
                 prefix: str,
                 expected_contents: RegexResolver):
        self._prefix = prefix
        self.expected_contents = expected_contents

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        prefix = ''
        if self._prefix:
            prefix = self._prefix + ' '
        return prefix + self._expected_obj_description(environment)

    def _expected_obj_description(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return 'todo'

    def _string_fragment(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return 'todo'


class _ErrorMessageResolverConstructor:
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: diff_msg_utils.ExpectedValueResolver,
                 ):
        self._expectation_type = expectation_type
        self._expected_value = expected_value

    def construct(self,
                  checked_file: FilePropertyDescriptorConstructor,
                  actual_info: ActualInfo) -> ErrorMessageResolver:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._expected_value,
                                     checked_file,
                                     actual_info)


class MatchesRegexStringMatcher(StringMatcher):
    def __init__(self,
                 expectation_type: ExpectationType,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 error_message_constructor: _ErrorMessageResolverConstructor,
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


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> List[str]:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: ExpectedValueResolver,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 actual_info: ActualInfo
                 ):
        self._expected_value = expected_value
        self._expectation_type = expectation_type
        self._checked_file_describer = checked_file_describer
        self._actual_info = actual_info

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        description_of_actual_file = self._checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        failure_info_resolver = DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            self._expected_value,
        )
        failure_info = failure_info_resolver.resolve(environment, self._actual_info)
        return failure_info.error_message()
