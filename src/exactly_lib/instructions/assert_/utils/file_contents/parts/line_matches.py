from typing import Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.instruction_arguments import LINE_MATCHER
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import CONTENTS_ATTRIBUTE
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.resolver_structure import LineMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.line_matcher.parse_line_matcher import parse_line_matcher_from_token_parser
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.line_matcher import LineMatcher, model_iter_from_file_line_iter
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def parse_any_line_matches_checker(expectation_type: ExpectationType,
                                   token_parser: TokenParser) -> FileContentsAssertionPart:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return assertion_part_for_any_line_matches(expectation_type,
                                               line_matcher_resolver)


def parse_every_line_matches_checker(expectation_type: ExpectationType,
                                     token_parser: TokenParser) -> FileContentsAssertionPart:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return assertion_part_for_every_line_matches(expectation_type,
                                                 line_matcher_resolver)


def _parse_line_matches_tokens_and_line_matcher(token_parser: TokenParser) -> LineMatcherResolver:
    token_parser.consume_mandatory_constant_unquoted_string(instruction_options.LINE_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(instruction_options.MATCHES_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.require_is_not_at_eol('Missing {_MATCHER_}')
    line_matcher_resolver = parse_line_matcher_from_token_parser(token_parser)
    token_parser.report_superfluous_arguments_if_not_at_eol()
    token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

    return line_matcher_resolver


def assertion_part_for_any_line_matches(expectation_type: ExpectationType,
                                        line_matcher_resolver: LineMatcherResolver) -> FileContentsAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _AnyLineMatchesAssertionPartForPositiveMatch(
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            expectation_type,
            line_matcher_resolver)
    else:
        return _AnyLineMatchesAssertionPartForNegativeMatch(
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            expectation_type,
            line_matcher_resolver)


def assertion_part_for_every_line_matches(expectation_type: ExpectationType,
                                          line_matcher_resolver: LineMatcherResolver) -> FileContentsAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _EveryLineMatchesAssertionPartForPositiveMatch(
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            expectation_type,
            line_matcher_resolver)
    else:
        return _EveryLineMatchesAssertionPartForNegativeMatch(
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
            expectation_type,
            line_matcher_resolver)


class FileContentsAssertionPart(FileContentsAssertionPart):
    def __init__(self,
                 any_or_every_keyword: str,
                 expectation_type: ExpectationType,
                 line_matcher_resolver: LineMatcherResolver):
        super().__init__()
        self._any_or_every_keyword = any_or_every_keyword
        self._expectation_type = expectation_type
        self._line_matcher_resolver = line_matcher_resolver

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._line_matcher_resolver.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_check: FileToCheck) -> FileToCheck:
        line_matcher = self._line_matcher_resolver.resolve(environment.symbols)
        self._check(environment, line_matcher, file_to_check)
        return file_to_check

    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        raise NotImplementedError('abstract method')

    def _report_fail(self,
                     environment: InstructionEnvironmentForPostSdsStep,
                     checked_file_describer: FilePropertyDescriptorConstructor,
                     actual_single_line_value: str,
                     description_lines: list = ()):
        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(err_msg_env_from_instr_env(environment),
                                                     diff_msg.actual_with_single_line_value(
                                                         actual_single_line_value,
                                                         description_lines))
        raise PfhFailException(failure_info.error_message())

    def _report_fail_with_line(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               checked_file_describer: FilePropertyDescriptorConstructor,
                               cause: str,
                               number__contents: str):
        single_line_actual_value = 'Line {} {}'.format(number__contents[0], cause)

        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(err_msg_env_from_instr_env(environment),
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
                instruction_options.LINE_ARGUMENT,
                instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                instruction_options.MATCHES_ARGUMENT,
                LINE_MATCHER.name])
            ))


class _AnyLineMatchesAssertionPartForPositiveMatch(FileContentsAssertionPart):
    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if line_matcher.matches(line):
                    return
        self._report_fail(environment,
                          file_to_check.describer,
                          'no line matches')


class _AnyLineMatchesAssertionPartForNegativeMatch(FileContentsAssertionPart):
    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if line_matcher.matches(line):
                    self._report_fail_with_line(environment,
                                                file_to_check.describer,
                                                'matches',
                                                line)


class _EveryLineMatchesAssertionPartForPositiveMatch(FileContentsAssertionPart):
    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if not line_matcher.matches(line):
                    self._report_fail_with_line(environment,
                                                file_to_check.describer,
                                                'does not match',
                                                line)


class _EveryLineMatchesAssertionPartForNegativeMatch(FileContentsAssertionPart):
    def _check(self,
               environment: InstructionEnvironmentForPostSdsStep,
               line_matcher: LineMatcher,
               file_to_check: FileToCheck):
        with file_to_check.lines() as file_lines:
            for line in model_iter_from_file_line_iter(file_lines):
                if not line_matcher.matches(line):
                    return
        self._report_fail(environment,
                          file_to_check.describer,
                          'every line matches')
