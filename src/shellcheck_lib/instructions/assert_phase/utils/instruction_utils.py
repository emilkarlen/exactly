import pathlib

from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.os_services import OsServices


class InstructionWithoutValidationBase(AssertPhaseInstruction):
    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class InstructionWithValidationOfRegularFileRelHomeBase(AssertPhaseInstruction):
    def __init__(self,
                 file_rel_home_name: str):
        self.file_rel_home_name = file_rel_home_name
        self._file_rel_home_path = None

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        self._file_rel_home_path = pathlib.Path(global_environment.home_directory / self.file_rel_home_name)
        if not self._file_rel_home_path.exists():
            return svh.new_svh_validation_error('File does not exist: ' + str(self._file_rel_home_path))
        if not self._file_rel_home_path.is_file():
            return svh.new_svh_validation_error('Not a regular file: ' + str(self._file_rel_home_path))
        return svh.new_svh_success()

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()

    @property
    def file_rel_home_path(self) -> pathlib.Path:
        return self._file_rel_home_path
