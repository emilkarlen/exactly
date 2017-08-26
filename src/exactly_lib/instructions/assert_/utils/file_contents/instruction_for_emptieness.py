from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg import diff_msg_utils
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.util.expectation_type import ExpectationType


class EmptinessAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_file: ComparisonActualFile):
        self.actual_file = actual_file
        self.expectation_type = expectation_type
        self.failure_info_resolver = diff_msg_utils.DiffFailureInfoResolver(
            actual_file.property_descriptor(),
            expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )

    def symbol_usages(self) -> list:
        return self.actual_file.references

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = self.actual_file.file_check_failure(environment)
        if failure_message:
            return pfh.new_pfh_fail(failure_message)

        size = self.actual_file.file_path(environment).stat().st_size
        if self.expectation_type is ExpectationType.POSITIVE:
            if size != 0:
                actual = str(size) + ' bytes'
                return self._new_failure(environment, actual)
        else:
            if size == 0:
                return self._new_failure(environment, EMPTINESS_CHECK_EXPECTED_VALUE)
        return pfh.new_pfh_pass()

    def _new_failure(self,
                     environment: i.InstructionEnvironmentForPostSdsStep,
                     actual: str,
                     ) -> pfh.PassOrFailOrHardError:
        return self.failure_info_resolver.resolve(
            environment,
            diff_msg.actual_with_single_line_value(actual)).as_pfh_fail()
