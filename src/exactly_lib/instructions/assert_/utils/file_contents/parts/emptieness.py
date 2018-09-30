from typing import Optional

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import CONTENTS_ATTRIBUTE
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import FileContentsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.string_matcher_assertion_part import \
    StringMatcherAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.instructions.utils.error_messages import err_msg_env_from_instr_env
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_matcher.resolvers import StringMatcherConstantResolver
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, ErrorMessageResolver
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import ExpectationType


def emptiness_via_string_matcher(expectation_type: ExpectationType) -> FileContentsAssertionPart:
    matcher_resolver = StringMatcherConstantResolver(
        EmptinessStringMatcher(expectation_type)
    )
    return StringMatcherAssertionPart(matcher_resolver)


class EmptinessContentsAssertionPartDEPRECATED(FileContentsAssertionPart):
    def __init__(self,
                 expectation_type: ExpectationType):
        super().__init__()
        self.expectation_type = expectation_type

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              custom_environment,
              file_to_check: FileToCheck) -> FileToCheck:
        """
        :return: processed_actual_file_path
        """
        mb_error_message = self._check(file_to_check)
        if mb_error_message is not None:
            raise PfhFailException(mb_error_message.resolve(err_msg_env_from_instr_env(environment)))
        return file_to_check

    def _check(self, file_to_check: FileToCheck) -> Optional[ErrorMessageResolver]:
        """
        :return: processed_actual_file_path
        """
        first_line = self._first_line(file_to_check)
        if self.expectation_type is ExpectationType.POSITIVE:
            if first_line != '':
                return _EqualityErrorMessageResolver(self.expectation_type,
                                                     file_to_check.describer,
                                                     repr(first_line) + '...')
        else:
            if first_line == '':
                return _EqualityErrorMessageResolver(self.expectation_type,
                                                     file_to_check.describer,
                                                     EMPTINESS_CHECK_EXPECTED_VALUE)
        return None

    @staticmethod
    def _first_line(file_to_check: FileToCheck) -> str:
        with file_to_check.lines() as lines:
            for line in lines:
                return line
        return ''


class _EqualityErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor,
                 actual: str,
                 ):
        self._expectation_type = expectation_type
        self._actual_file_prop_descriptor_constructor = actual_file_prop_descriptor_constructor
        self._actual = actual

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        diff_failure_info_resolver = self._failure_info_resolver(self._actual_file_prop_descriptor_constructor)
        failure_info = diff_failure_info_resolver.resolve(environment,
                                                          diff_msg.actual_with_single_line_value(self._actual))
        return failure_info.error_message()

    def _failure_info_resolver(self,
                               actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor
                               ) -> diff_msg_utils.DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            actual_file_prop_descriptor_constructor.construct_for_contents_attribute(CONTENTS_ATTRIBUTE),
            self._expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )
