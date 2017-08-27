import pathlib

from exactly_lib.instructions.assert_.utils.checker import Checker
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.instruction_with_checkers import \
    AssertionInstructionWithChecker
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver
from exactly_lib.util.expectation_type import ExpectationType


class EmptinessChecker(Checker):
    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_file: ComparisonActualFile):
        super().__init__()
        self.actual_file = actual_file
        self.expectation_type = expectation_type
        self.failure_info_resolver = diff_msg_utils.DiffFailureInfoResolver(
            actual_file.property_descriptor(),
            expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )

    @property
    def references(self) -> list:
        return self.actual_file.references

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


def emptiness_assertion_instruction(expectation_type: ExpectationType,
                                    actual_file: ComparisonActualFile,
                                    actual_file_transformer_resolver: FileTransformerResolver,
                                    ) -> AssertPhaseInstruction:
    return AssertionInstructionWithChecker(
        actual_file,
        actual_file_transformer_resolver,
        EmptinessChecker(expectation_type, actual_file))
