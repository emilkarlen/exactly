import re
import shlex
from typing import Optional, Pattern, Match, Set

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.error_messages import ExpectedValueResolver, ErrorMessageResolverConstructor
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.test_case_utils.string_matcher import matcher_options, resolvers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher, StringMatcherValue
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
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
    error_message_constructor = ErrorMessageResolverConstructor(
        expectation_type,
        ExpectedValueResolver(matcher_options.MATCHES_ARGUMENT,
                              contents_matcher)
    )

    def get_value_validator(symbols: SymbolTable) -> PreOrPostSdsValueValidator:
        return contents_matcher.resolve(symbols).validator()

    def get_value(symbols: SymbolTable) -> StringMatcherValue:
        regex_value = contents_matcher.resolve(symbols)
        return MatchesRegexStringMatcherValue(
            expectation_type,
            regex_value,
            is_full_match,
            error_message_constructor,
        )

    return resolvers.StringMatcherResolverFromParts2(
        contents_matcher.references,
        pre_or_post_validation.PreOrPostSdsValidatorFromValueValidator(get_value_validator),
        get_value,
    )


class MatchesRegexStringMatcher(StringMatcher):
    NAME = ' '.join((
        matcher_options.MATCHES_ARGUMENT,
        syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 expectation_type: ExpectationType,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 error_message_constructor: ErrorMessageResolverConstructor,
                 ):
        super().__init__()
        self._expectation_type = expectation_type
        self._is_full_match = is_full_match
        self._pattern = pattern
        self._err_msg_constructor = error_message_constructor
        self._pattern_renderer = custom_details.PatternRenderer(pattern)
        self._expected_detail_renderer = custom_details.expected(
            custom_details.regex_with_config_renderer(
                is_full_match,
                self._pattern_renderer,
            )
        )

    @property
    def name(self) -> str:
        return ' '.join((
            matcher_options.MATCHES_ARGUMENT,
            syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
        ))

    @staticmethod
    def new_structure_tree(is_full_match: bool,
                           expected_regex: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            MatchesRegexStringMatcher.NAME,
            None,
            (custom_details.regex_with_config_renderer(is_full_match, expected_regex),),
            (),
        )

    def _structure(self) -> StructureRenderer:
        return self.new_structure_tree(
            self._is_full_match,
            self._pattern_renderer,
        )

    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self._expectation_type) + matcher_options.MATCHES_ARGUMENT

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        actual_contents = self._actual_contents(model)
        match = self._find_match(actual_contents)
        if match is None:
            if self._expectation_type is ExpectationType.POSITIVE:
                return self._err_msg_resolver(actual_contents)
            else:
                return None
        else:
            if self._expectation_type is ExpectationType.POSITIVE:
                return None
            else:
                return self._err_msg_resolver(actual_contents)

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        if self._expectation_type is ExpectationType.NEGATIVE:
            positive_matcher = MatchesRegexStringMatcher(ExpectationType.POSITIVE,
                                                         self._is_full_match,
                                                         self._pattern,
                                                         self._err_msg_constructor)
            return combinator_matchers.Negation(positive_matcher).matches_w_trace(model)
        else:
            return self._matches_positive(model)

    def _matches_positive(self, model: FileToCheck) -> MatchingResult:
        actual_contents = self._actual_contents(model)

        tb = self._new_tb_with_expected().append_details(
            custom_details.actual(
                custom_details.StringAsSingleLineWithMaxLenDetailsRenderer(actual_contents))
        )

        match = self._find_match(actual_contents)

        if match is not None:
            tb.append_details(
                custom_details.match(custom_details.PatternMatchRenderer(match))
            )

        return tb.build_result(match is not None)

    def _find_match(self, actual_contents: str) -> Optional[Match]:
        if self._is_full_match:
            return self._pattern.fullmatch(actual_contents)
        else:
            return self._pattern.search(actual_contents)

    @staticmethod
    def _actual_contents(model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(lines)

    def _err_msg_resolver(self, actual_contents: str) -> ErrorMessageResolver:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._is_full_match,
                                     self._pattern,
                                     actual_contents)

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)


class MatchesRegexStringMatcherValue(StringMatcherValue):
    def __init__(self,
                 expectation_type: ExpectationType,
                 regex: RegexValue,
                 is_full_match: bool,
                 error_message_constructor: ErrorMessageResolverConstructor,
                 ):
        self._expectation_type = expectation_type
        self._regex = regex
        self._is_full_match = is_full_match
        self._error_message_constructor = error_message_constructor

    def structure(self) -> StructureRenderer:
        return MatchesRegexStringMatcher.new_structure_tree(
            self._is_full_match,
            self._regex.describer(),
        )

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._regex.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._regex.validator()

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        return MatchesRegexStringMatcher(
            self._expectation_type,
            self._is_full_match,
            self._regex.value_when_no_dir_dependencies(),
            self._error_message_constructor,
        )

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringMatcher:
        return MatchesRegexStringMatcher(
            self._expectation_type,
            self._is_full_match,
            self._regex.value_of_any_dependency(tcds),
            self._error_message_constructor,
        )


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 is_full_match: bool,
                 pattern: Pattern[str],
                 actual_contents: str,
                 ):
        self._expectation_type = expectation_type
        self._is_full_match = is_full_match
        self._pattern = pattern
        self._actual_contents = actual_contents

    def resolve(self) -> str:
        regex_line = self._header() + self._flags_string() + shlex.quote(self._pattern.pattern)
        return regex_line + '\nIn:\n' + self._contents_lines()

    def _contents_lines(self) -> str:
        if not self._actual_contents:
            return '<empty string>'
        lines = self._actual_contents.split(sep='\n', maxsplit=_ERR_MSG_MAX_NUM_LINES_TO_DISPLAY)

        if len(lines) > _ERR_MSG_MAX_NUM_LINES_TO_DISPLAY:
            lines[-1] = '...'

        return '\n'.join(lines)

    def _header(self) -> str:
        start = ('Found no match of '
                 if self._expectation_type is ExpectationType.POSITIVE
                 else 'Found match of ')
        return start + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name + ' '

    def _flags_string(self) -> str:
        flags = []
        if self._is_full_match:
            flags.append(matcher_options.FULL_MATCH_ARGUMENT_OPTION.long)
        if self._pattern.flags & re.IGNORECASE:
            flags.append(parse_regex.IGNORE_CASE_OPTION_NAME.long)

        return (
            '(' + ','.join(flags) + ') '
            if flags
            else ''
        )
