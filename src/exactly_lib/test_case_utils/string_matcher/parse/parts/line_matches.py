from typing import Set, Optional, Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.definitions.instruction_arguments import LINE_MATCHER
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import LineMatcherResolver, StringMatcherResolver
from exactly_lib.test_case.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.line_matcher.parse_line_matcher import parse_line_matcher_from_token_parser
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherResolverFromParts
from exactly_lib.test_case_utils.symbols_utils import resolving_dependencies_from_references
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor, ErrorMessageResolver, \
    ErrorMessageResolvingEnvironment, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher, model_iter_from_file_line_iter
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def parse_any_line_matches_matcher(expectation_type: ExpectationType,
                                   token_parser: TokenParser) -> StringMatcherResolver:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return matcher_for_any_line_matches(expectation_type,
                                        line_matcher_resolver)


def parse_every_line_matches_matcher(expectation_type: ExpectationType,
                                     token_parser: TokenParser) -> StringMatcherResolver:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return matcher_for_every_line_matches(expectation_type,
                                          line_matcher_resolver)


def _parse_line_matches_tokens_and_line_matcher(token_parser: TokenParser) -> LineMatcherResolver:
    token_parser.consume_mandatory_constant_unquoted_string(matcher_options.LINE_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.require_is_not_at_eol('Missing {_MATCHER_}')
    line_matcher_resolver = parse_line_matcher_from_token_parser(token_parser)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

    return line_matcher_resolver


def matcher_for_any_line_matches(expectation_type: ExpectationType,
                                 line_matcher_resolver: LineMatcherResolver) -> StringMatcherResolver:
    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        err_msg_env = ErrorMessageResolvingEnvironment(environment.home_and_sds,
                                                       environment.symbols)
        if expectation_type is ExpectationType.POSITIVE:
            return _AnyLineMatchesStringMatcherForPositiveMatch(
                instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
                expectation_type,
                line_matcher_resolver.resolve(environment.symbols),
                err_msg_env)
        else:
            return _AnyLineMatchesStringMatcherForNegativeMatch(
                instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
                expectation_type,
                line_matcher_resolver.resolve(environment.symbols),
                err_msg_env)

    def get_resolving_dependencies(symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_references(line_matcher_resolver.references, symbols)

    return StringMatcherResolverFromParts(
        line_matcher_resolver.references,
        ConstantSuccessValidator(),
        get_resolving_dependencies,
        get_matcher,
    )


def matcher_for_every_line_matches(expectation_type: ExpectationType,
                                   line_matcher_resolver: LineMatcherResolver) -> StringMatcherResolver:
    def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> StringMatcher:
        err_msg_env = ErrorMessageResolvingEnvironment(environment.home_and_sds,
                                                       environment.symbols)
        if expectation_type is ExpectationType.POSITIVE:
            return _EveryLineMatchesStringMatcherForPositiveMatch(
                instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
                expectation_type,
                line_matcher_resolver.resolve(environment.symbols),
                err_msg_env)
        else:
            return _EveryLineMatchesStringMatcherForNegativeMatch(
                instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
                expectation_type,
                line_matcher_resolver.resolve(environment.symbols),
                err_msg_env)

    def get_resolving_dependencies(symbols: SymbolTable) -> Set[DirectoryStructurePartition]:
        return resolving_dependencies_from_references(line_matcher_resolver.references, symbols)

    return StringMatcherResolverFromParts(
        line_matcher_resolver.references,
        ConstantSuccessValidator(),
        get_resolving_dependencies,
        get_matcher,
    )


class _StringMatcherBase(StringMatcher):
    def __init__(self,
                 any_or_every_keyword: str,
                 expectation_type: ExpectationType,
                 line_matcher: LineMatcher,
                 err_msg_environment: ErrorMessageResolvingEnvironment):
        super().__init__()
        self._any_or_every_keyword = any_or_every_keyword
        self._expectation_type = expectation_type
        self._line_matcher = line_matcher
        self._err_msg_environment = err_msg_environment

    @property
    def option_description(self) -> str:
        components = [self._any_or_every_keyword,
                      matcher_options.LINE_ARGUMENT,
                      instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                      self._line_matcher.option_description]
        return ' '.join(components)

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        try:
            self._check(self._line_matcher, model)
        except PfhFailException as ex:
            return ConstantErrorMessageResolver(ex.err_msg)

    def _check(self,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        raise NotImplementedError('abstract method')

    def _report_fail(self,
                     checked_file_describer: FilePropertyDescriptorConstructor,
                     actual_single_line_value: str,
                     description_lines: Sequence[str] = ()):
        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(self._err_msg_environment,
                                                     diff_msg.actual_with_single_line_value(
                                                         actual_single_line_value,
                                                         description_lines))
        raise PfhFailException(failure_info.error_message())

    def _report_fail_with_line(self,
                               checked_file_describer: FilePropertyDescriptorConstructor,
                               cause: str,
                               number__contents: str):
        single_line_actual_value = 'Line {} {}'.format(number__contents[0], cause)

        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(self._err_msg_environment,
                                                     diff_msg.actual_with_single_line_value(
                                                         single_line_actual_value,
                                                         [number__contents[1]]))
        raise PfhFailException(failure_info.error_message())

    def _diff_failure_info_resolver(self,
                                    checked_file_describer: FilePropertyDescriptorConstructor
                                    ) -> DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE),
            self._expectation_type,
            diff_msg_utils.expected_constant(' '.join([
                self._any_or_every_keyword,
                matcher_options.LINE_ARGUMENT,
                instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                LINE_MATCHER.name])
            ))


class _AnyLineMatchesStringMatcherForPositiveMatch(_StringMatcherBase):
    def _check(self,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if line_matcher.matches(line):
                    return
        self._report_fail(file_to_check.describer,
                          'no line matches')


class _AnyLineMatchesStringMatcherForNegativeMatch(_StringMatcherBase):
    def _check(self,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if line_matcher.matches(line):
                    self._report_fail_with_line(file_to_check.describer,
                                                'matches',
                                                line)


class _EveryLineMatchesStringMatcherForPositiveMatch(_StringMatcherBase):
    def _check(self,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if not line_matcher.matches(line):
                    self._report_fail_with_line(file_to_check.describer,
                                                'does not match',
                                                line)


class _EveryLineMatchesStringMatcherForNegativeMatch(_StringMatcherBase):
    def _check(self,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if not line_matcher.matches(line):
                    return
        self._report_fail(file_to_check.describer,
                          'every line matches')
