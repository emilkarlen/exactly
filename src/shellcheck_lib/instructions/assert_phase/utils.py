import pathlib

from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction


class InstructionWithoutValidationBase(AssertPhaseInstruction):
    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        return i.new_svh_success()

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        raise NotImplementedError()


class InstructionWithValidationOfRegularFileRelHomeBase(AssertPhaseInstruction):
    def __init__(self,
                 file_rel_home_name: str):
        self.file_rel_home_name = file_rel_home_name
        self._file_rel_home_path = None

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> i.SuccessOrValidationErrorOrHardError:
        self._file_rel_home_path = pathlib.Path(global_environment.home_directory / self.file_rel_home_name)
        if not self._file_rel_home_path.exists():
            return i.new_svh_validation_error('File does not exist: ' + str(self._file_rel_home_path))
        if not self._file_rel_home_path.is_file():
            return i.new_svh_validation_error('Not a regular file: ' + str(self._file_rel_home_path))
        return i.new_svh_success()

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        raise NotImplementedError()

    @property
    def file_rel_home_path(self) -> pathlib.Path:
        return self._file_rel_home_path
