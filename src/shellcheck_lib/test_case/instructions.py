from enum import Enum
import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.script_language import act_script_management


ENV_VAR_HOME = 'SHELLTEST_HOME'
ENV_VAR_TEST = 'SHELLTEST_TESTROOT'
ENV_VAR_TMP = 'SHELLTEST_TMP'

ALL_ENV_VARS = [ENV_VAR_HOME,
                ENV_VAR_TEST,
                ENV_VAR_TMP]


class SuccessOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                failure_message: str):
        return tuple.__new__(cls, (failure_message, ))

    @property
    def failure_message(self) -> str:
        """
        :return None iff the object represents SUCCESS.
        """
        return self[0]

    @property
    def is_success(self) -> bool:
        return self[0] is None

    @property
    def is_hard_error(self) -> bool:
        return not self.is_success


class SuccessOrValidationErrorOrHardError(tuple):
    def __new__(cls,
                is_hard_error: bool,
                failure_message: str):
        return tuple.__new__(cls, (is_hard_error, failure_message, ))

    @property
    def failure_message(self) -> str:
        """
        :return None iff the object represents SUCCESS.
        """
        return self[1]

    @property
    def is_success(self) -> bool:
        return self[0] is None

    @property
    def is_validation_error(self) -> bool:
        return self[0] is False

    @property
    def is_hard_error(self) -> bool:
        return self[0] is True


class PassOrFailOrHardErrorEnum(Enum):
    """
    Implementation note: The error-values must correspond to those of PartialControlledFailureEnum
    """
    PASS = 0
    FAIL = 2
    HARD_ERROR = 99


class PassOrFailOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                status: PassOrFailOrHardErrorEnum,
                failure_message: str):
        return tuple.__new__(cls, (status, failure_message, ))

    @property
    def status(self) -> PassOrFailOrHardErrorEnum:
        return self[0]

    @property
    def is_error(self) -> bool:
        return self.status is not PassOrFailOrHardErrorEnum.PASS

    @property
    def failure_message(self) -> str:
        """
        :return None iff the object represents PASS.
        """
        return self[1]


class ExecutionMode(Enum):
    NORMAL = 0
    SKIPPED = 1
    XFAIL = 2


class PhaseEnvironmentForAnonymousPhase:
    def __init__(self, home_dir_path: pathlib.Path):
        self.__home_dir_path = home_dir_path
        self.__execution_mode = ExecutionMode.NORMAL

    @property
    def execution_mode(self) -> ExecutionMode:
        return self.__execution_mode

    def set_execution_mode(self,
                           x: ExecutionMode):
        self.__execution_mode = x

    @property
    def home_dir(self) -> str:
        return str(self.__home_dir_path)

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self.__home_dir_path

    def set_home_dir(self, x: pathlib.Path):
        self.__home_dir_path = x


class PhaseEnvironmentForScriptGeneration:
    """
    The phase-environment for phases that generate a script.
    """

    def __init__(self,
                 script_source_accumulator: act_script_management.ScriptSourceAccumulator):
        self.__script_source_accumulator = script_source_accumulator

    @property
    def append(self) -> act_script_management.ScriptSourceAccumulator:
        return self.__script_source_accumulator


class PhaseEnvironmentForInternalCommands:
    """
    The phase-environment for phases that are implemented internally
    - in Python.
    """

    def __init__(self):
        pass


class GlobalEnvironmentForPreEdsStep:
    def __init__(self,
                 home_dir: pathlib.Path):
        self.__home_dir = home_dir

    @property
    def home_directory(self) -> pathlib.Path:
        return self.__home_dir


class GlobalEnvironmentForPostEdsPhase(GlobalEnvironmentForPreEdsStep):
    def __init__(self,
                 home_dir: pathlib.Path,
                 eds: ExecutionDirectoryStructure):
        super().__init__(home_dir)
        self.__eds = eds

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.__eds


class SetupSettingsBuilder:
    def __init__(self,
                 stdin_file_name: str=None):
        self.__stdin_file_name = stdin_file_name

    def set_stdin_file(self,
                       file_name: str):
        self.__stdin_file_name = file_name

    @property
    def stdin_file_name(self) -> str:
        return self.__stdin_file_name

    @stdin_file_name.setter
    def stdin_file_name(self, x: str):
        self.__stdin_file_name = x


class AnonymousPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the anonymous phase.
    """

    def main(self,
             global_environment,
             phase_environment: PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class InternalInstruction(Instruction):
    """
    Abstract base class for instructions that are implemented in python.
    """

    def execute(self,
                phase_name: str,
                global_environment: GlobalEnvironmentForPostEdsPhase,
                phase_environment: PhaseEnvironmentForInternalCommands):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class SetupPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the SETUP phase.
    """

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        """
        raise NotImplementedError()

    def post_validate(self,
                      global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()


class ActPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ACT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForScriptGeneration) -> SuccessOrHardError:
        """
        Builds the script, and sets some execution premises (e.g. stdin),
        by updating the phase environment.

        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class AssertPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """

    def validate(self,
                 global_environment: GlobalEnvironmentForPostEdsPhase) -> SuccessOrValidationErrorOrHardError:
        raise NotImplementedError()

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForInternalCommands) -> PassOrFailOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class CleanupPhaseInstruction(Instruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """

    def main(self,
             global_environment: GlobalEnvironmentForPostEdsPhase,
             phase_environment: PhaseEnvironmentForInternalCommands) -> SuccessOrHardError:
        """
        Does whatever this instruction should do.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()
