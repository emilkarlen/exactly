from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import CONTENTS_ATTRIBUTE, \
    FilePropertyDescriptorConstructor
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import ActualFileAssertionPart, \
    FileToCheck
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.util.expectation_type import ExpectationType


def assertion_part_for_any_line_matches(expectation_type: ExpectationType,
                                        expected_reg_ex,
                                        reg_ex_arg_source_string: str) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _AnyLineMatchesAssertionPartForPositiveMatch(instruction_options.ANY_LINE_ARGUMENT,
                                                            expectation_type,
                                                            expected_reg_ex,
                                                            reg_ex_arg_source_string)
    else:
        return _AnyLineMatchesAssertionPartForNegativeMatch(instruction_options.ANY_LINE_ARGUMENT,
                                                            expectation_type,
                                                            expected_reg_ex,
                                                            reg_ex_arg_source_string)


def assertion_part_for_every_line_matches(expectation_type: ExpectationType,
                                          expected_reg_ex,
                                          reg_ex_arg_source_string: str) -> ActualFileAssertionPart:
    if expectation_type is ExpectationType.POSITIVE:
        return _EveryLineMatchesAssertionPartForPositiveMatch(instruction_options.EVERY_LINE_ARGUMENT,
                                                              expectation_type,
                                                              expected_reg_ex,
                                                              reg_ex_arg_source_string)
    else:
        return _EveryLineMatchesAssertionPartForNegativeMatch(instruction_options.EVERY_LINE_ARGUMENT,
                                                              expectation_type,
                                                              expected_reg_ex,
                                                              reg_ex_arg_source_string)


class FileAssertionPart(ActualFileAssertionPart):
    def __init__(self,
                 any_or_every_keyword: str,
                 expectation_type: ExpectationType,
                 expected_reg_ex,
                 reg_ex_arg_source_string: str):
        super().__init__()
        self._any_or_every_keyword = any_or_every_keyword
        self._expectation_type = expectation_type
        self._expected_reg_ex = expected_reg_ex
        self._reg_ex_arg_source_string = reg_ex_arg_source_string

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        raise NotImplementedError('abstract method')

    def _report_fail(self,
                     environment: InstructionEnvironmentForPostSdsStep,
                     checked_file_describer: FilePropertyDescriptorConstructor,
                     actual_single_line_value: str,
                     description_lines: list = ()):
        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(environment,
                                                     diff_msg.actual_with_single_line_value(
                                                         actual_single_line_value,
                                                         description_lines))
        raise PfhFailException(failure_info.render())

    def _report_fail_with_line(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               checked_file_describer: FilePropertyDescriptorConstructor,
                               line_number: int,
                               cause: str,
                               line_contents: str):
        single_line_actual_value = 'Line {} {}'.format(line_number, cause)

        failure_info_resolver = self._diff_failure_info_resolver(checked_file_describer)
        failure_info = failure_info_resolver.resolve(environment,
                                                     diff_msg.actual_with_single_line_value(
                                                         single_line_actual_value,
                                                         [line_contents]))
        raise PfhFailException(failure_info.render())

    def _diff_failure_info_resolver(self,
                                    checked_file_describer: FilePropertyDescriptorConstructor
                                    ) -> DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE),
            self._expectation_type,
            diff_msg_utils.expected_constant(' '.join([
                self._any_or_every_keyword,
                instruction_options.LINE_ARGUMENT,
                instruction_options.MATCHES_ARGUMENT,
                instruction_arguments.REG_EX.name,
                self._reg_ex_arg_source_string])
            ))


class _AnyLineMatchesAssertionPartForPositiveMatch(FileAssertionPart):
    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        with file_to_check.lines() as lines:
            for line in lines:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return file_to_check
        self._report_fail(environment,
                          file_to_check.checked_file_describer,
                          'no line matches')


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
                    self._report_fail_with_line(environment,
                                                file_to_check.checked_file_describer,
                                                line_num,
                                                'matches',
                                                line)
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
                                                file_to_check.checked_file_describer,
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
        self._report_fail(environment,
                          file_to_check.checked_file_describer,
                          'every line matches')
