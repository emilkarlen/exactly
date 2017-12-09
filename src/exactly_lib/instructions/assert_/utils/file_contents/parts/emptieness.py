from exactly_lib.instructions.assert_.utils.file_contents.actual_files import FilePropertyDescriptorConstructor, \
    CONTENTS_ATTRIBUTE
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart, \
    FileToCheck
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.util.logic_types import ExpectationType


class EmptinessContentsAssertionPart(FileContentsAssertionPart):
    def __init__(self,
                 expectation_type: ExpectationType):
        super().__init__()
        self.expectation_type = expectation_type

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: FileToCheck) -> FileToCheck:
        """
        :return: processed_actual_file_path
        """
        first_line = self._first_line(file_to_check)
        if self.expectation_type is ExpectationType.POSITIVE:
            if first_line != '':
                return self._raise_fail(environment,
                                        file_to_check.describer,
                                        repr(first_line) + '...')
        else:
            if first_line == '':
                return self._raise_fail(environment,
                                        file_to_check.describer,
                                        EMPTINESS_CHECK_EXPECTED_VALUE)
        return file_to_check

    def _raise_fail(self,
                    environment: i.InstructionEnvironmentForPostSdsStep,
                    actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor,
                    actual: str,
                    ):
        diff_failure_info_resolver = self._failure_info_resolver(actual_file_prop_descriptor_constructor)
        failure_info = diff_failure_info_resolver.resolve(environment,
                                                          diff_msg.actual_with_single_line_value(actual))
        raise PfhFailException(failure_info.error_message())

    @staticmethod
    def _first_line(file_to_check: FileToCheck) -> str:
        with file_to_check.lines() as lines:
            for line in lines:
                return line
        return ''

    def _failure_info_resolver(self,
                               actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor
                               ) -> diff_msg_utils.DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            actual_file_prop_descriptor_constructor.construct_for_contents_attribute(CONTENTS_ATTRIBUTE),
            self.expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )
