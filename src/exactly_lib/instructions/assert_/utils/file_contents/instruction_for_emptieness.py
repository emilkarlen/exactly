import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    ActualFileAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.util.expectation_type import ExpectationType


class EmptinessChecker(ActualFileAssertionPart):
    def __init__(self,
                 expectation_type: ExpectationType,
                 description_of_actual_file: PropertyDescriptor):
        super().__init__()
        self.expectation_type = expectation_type
        self.failure_info_resolver = diff_msg_utils.DiffFailureInfoResolver(
            description_of_actual_file,
            expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path
              ) -> pathlib.Path:
        """
        :return: processed_actual_file_path
        """
        size = file_to_check.stat().st_size
        if self.expectation_type is ExpectationType.POSITIVE:
            if size != 0:
                actual = str(size) + ' bytes'
                return self._raise_fail(environment, actual)
        else:
            if size == 0:
                return self._raise_fail(environment, EMPTINESS_CHECK_EXPECTED_VALUE)

    def _raise_fail(self,
                    environment: i.InstructionEnvironmentForPostSdsStep,
                    actual: str,
                    ):
        failure_info = self.failure_info_resolver.resolve(environment,
                                                          diff_msg.actual_with_single_line_value(actual))
        raise PfhFailException(failure_info.render())
