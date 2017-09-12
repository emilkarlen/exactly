import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import ActualFileAssertionPart
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.util.expectation_type import ExpectationType


def checker_for_any_line_matches(expectation_type: ExpectationType,
                                 failure_info_resolver: DiffFailureInfoResolver,
                                 expected_reg_ex) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _AnyLineMatchesCheckerForPositiveMatch(failure_info_resolver, expected_reg_ex)
    else:
        return _AnyLineMatchesCheckerForNegativeMatch(failure_info_resolver, expected_reg_ex)


def checker_for_every_line_matches(expectation_type: ExpectationType,
                                   failure_info_resolver: DiffFailureInfoResolver,
                                   expected_reg_ex) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _EveryLineMatchesCheckerForPositiveMatch(failure_info_resolver, expected_reg_ex)
    else:
        return _EveryLineMatchesCheckerForNegativeMatch(failure_info_resolver, expected_reg_ex)


class FileChecker(ActualFileAssertionPart):
    def __init__(self,
                 failure_info_resolver: DiffFailureInfoResolver,
                 expected_reg_ex):
        super().__init__()
        self._failure_info_resolver = failure_info_resolver
        self._expected_reg_ex = expected_reg_ex

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path):
        raise NotImplementedError()

    def _report_fail(self,
                     environment: InstructionEnvironmentForPostSdsStep,
                     actual_single_line_value: str,
                     description_lines: list = ()):
        failure_info = self._failure_info_resolver.resolve(environment,
                                                           diff_msg.actual_with_single_line_value(
                                                               actual_single_line_value,
                                                               description_lines))
        raise PfhFailException(failure_info.render())

    def _report_fail_with_line(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               line_number: int,
                               cause: str,
                               line_contents: str):
        single_line_actual_value = 'Line {} {}'.format(line_number, cause)

        failure_info = self._failure_info_resolver.resolve(environment,
                                                           diff_msg.actual_with_single_line_value(
                                                               single_line_actual_value,
                                                               [line_contents]))
        raise PfhFailException(failure_info.render())


class _AnyLineMatchesCheckerForPositiveMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path):
        actual_file_name = str(file_to_check)
        with open(actual_file_name) as f:
            for line in f:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return
        self._report_fail(environment, 'no line matches')


class _AnyLineMatchesCheckerForNegativeMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path):
        actual_file_name = str(file_to_check)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                plain_line = line.rstrip('\n')
                if self._expected_reg_ex.search(plain_line):
                    self._report_fail_with_line(environment, line_num, 'matches', line)
                line_num += 1


class _EveryLineMatchesCheckerForPositiveMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path):
        actual_file_name = str(file_to_check)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                if not self._expected_reg_ex.search(line.rstrip('\n')):
                    self._report_fail_with_line(environment,
                                                line_num,
                                                'does not match',
                                                line)
                line_num += 1


class _EveryLineMatchesCheckerForNegativeMatch(FileChecker):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path):
        actual_file_name = str(file_to_check)
        with open(actual_file_name) as f:
            line_num = 1
            for line in f:
                plain_line = line.rstrip('\n')
                if not self._expected_reg_ex.search(plain_line):
                    return
                line_num += 1
        self._report_fail(environment, 'every line matches')
