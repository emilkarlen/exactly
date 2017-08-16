from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.utils.err_msg import diff_msg
from exactly_lib.instructions.utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.instructions.utils.expectation_type import from_is_negated
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh


class EmptinessAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 expect_empty: bool,
                 actual_file: ComparisonActualFile):
        self.actual_file = actual_file
        self.expect_empty = expect_empty
        self.failure_info_resolver = DiffFailureInfoResolver(
            actual_file.property_descriptor(),
            from_is_negated(not expect_empty),
            EMPTINESS_CHECK_EXPECTED_VALUE,
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
        if self.expect_empty:
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
        return self.failure_info_resolver.resolve_pfh_fail(
            environment,
            diff_msg.actual_with_single_line_value(actual))
