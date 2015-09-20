import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure

ENV_VAR_HOME = 'SHELLCHECK_HOME'
ENV_VAR_TEST = 'SHELLCHECK_TESTROOT'
ENV_VAR_TMP = 'SHELLCHECK_TMP'

ALL_ENV_VARS = [ENV_VAR_HOME,
                ENV_VAR_TEST,
                ENV_VAR_TMP]


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
