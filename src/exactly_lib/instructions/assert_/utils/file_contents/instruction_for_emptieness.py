from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
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

    def symbol_usages(self) -> list:
        return self.actual_file.symbol_usages

    def main(self,
             environment: i.InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        failure_message = self.actual_file.file_check_failure(environment)
        if failure_message:
            return pfh.new_pfh_fail(failure_message)

        size = self.actual_file.file_path(environment).stat().st_size
        if self.expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()
