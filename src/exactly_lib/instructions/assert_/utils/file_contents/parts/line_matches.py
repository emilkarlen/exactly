from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import ActualFileAssertionPart, \
    FileToCheck
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.util.expectation_type import ExpectationType


def assertion_part_for_any_line_matches(expectation_type: ExpectationType,
                                        failure_info_resolver: DiffFailureInfoResolver,
                                        expected_reg_ex) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _AnyLineMatchesAssertionPartForPositiveMatch(failure_info_resolver, expected_reg_ex)
    else:
        return _AnyLineMatchesAssertionPartForNegativeMatch(failure_info_resolver, expected_reg_ex)


def assertion_part_for_every_line_matches(expectation_type: ExpectationType,
                                          failure_info_resolver: DiffFailureInfoResolver,
                                          expected_reg_ex) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _EveryLineMatchesAssertionPartForPositiveMatch(failure_info_resolver, expected_reg_ex)
    else:
        return _EveryLineMatchesAssertionPartForNegativeMatch(failure_info_resolver, expected_reg_ex)


class FileAssertionPart(ActualFileAssertionPart):
    def __init__(self,
                 failure_info_resolver: DiffFailureInfoResolver,
                 expected_reg_ex):
        super().__init__()
        self._failure_info_resolver = failure_info_resolver
        self._expected_reg_ex = expected_reg_ex

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
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


class _AnyLineMatchesAssertionPartForPositiveMatch(FileAssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        with file_to_check.lines() as lines:
            for line in lines:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return file_to_check
        self._report_fail(environment, 'no line matches')


class _AnyLineMatchesAssertionPartForNegativeMatch(FileAssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        with file_to_check.lines() as lines:
            line_num = 1
            for line in lines:
                plain_line = line.rstrip('\n')
                if self._expected_reg_ex.search(plain_line):
                    self._report_fail_with_line(environment, line_num, 'matches', line)
                line_num += 1
        return file_to_check


class _EveryLineMatchesAssertionPartForPositiveMatch(FileAssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        with file_to_check.lines() as lines:
            line_num = 1
            for line in lines:
                if not self._expected_reg_ex.search(line.rstrip('\n')):
                    self._report_fail_with_line(environment,
                                                line_num,
                                                'does not match',
                                                line)
                line_num += 1
        return file_to_check


class _EveryLineMatchesAssertionPartForNegativeMatch(FileAssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        with file_to_check.lines() as lines:
            line_num = 1
            for line in lines:
                plain_line = line.rstrip('\n')
                if not self._expected_reg_ex.search(plain_line):
                    return file_to_check
                line_num += 1
        self._report_fail(environment, 'every line matches')
