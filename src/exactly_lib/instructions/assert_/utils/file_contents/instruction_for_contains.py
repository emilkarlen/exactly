import pathlib

from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.result import pfh


class ContainsAssertionInstruction(AssertPhaseInstruction):
    def __init__(self,
                 expected_reg_ex,
                 actual_contents: ComparisonActualFile):
        self._actual_value = actual_contents
        self._expected_reg_ex = expected_reg_ex

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        actual_file_path = self._actual_value.file_path(environment)
        failure_message = self._actual_value.file_check_failure(environment)
        if failure_message is not None:
            return pfh.new_pfh_fail(failure_message)

        processed_actual_file_path = self._get_processed_actual_file_path(actual_file_path,
                                                                          environment,
                                                                          os_services)
        actual_file_name = str(processed_actual_file_path)
        with open(actual_file_name) as f:
            for line in f:
                if self._expected_reg_ex.search(line.rstrip('\n')):
                    return pfh.new_pfh_pass()
        return pfh.new_pfh_fail('No lines matching ' + str(self._expected_reg_ex))

    def _get_processed_actual_file_path(self,
                                        actual_file_path: pathlib.Path,
                                        environment: i.InstructionEnvironmentForPostSdsStep,
                                        os_services: OsServices) -> pathlib.Path:
        return actual_file_path
