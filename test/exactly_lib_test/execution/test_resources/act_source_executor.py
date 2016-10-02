import pathlib

from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError, ActSourceAndExecutor
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class ActSourceExecutorThatRunsConstantActions(ActSourceExecutor):
    def __init__(self,
                 validate_test_action,
                 prepare_test_action,
                 execute_test_action):
        self.__validate_test_action = validate_test_action
        self.__prepare_test_action = prepare_test_action
        self.__execute_test_action = execute_test_action

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_test_action()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        return self.__prepare_test_action()

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.__execute_test_action()


class ActSourceAndExecutorThatRunsConstantActions(ActSourceAndExecutor):
    def __init__(self,
                 prepare_action,
                 execute_action):
        self.__prepare_action = prepare_action
        self.__execute_action = execute_action

    def prepare(self, home_and_eds: HomeAndEds) -> sh.SuccessOrHardError:
        return self.__prepare_action()

    def execute(self, home_and_eds: HomeAndEds, std_files: StdFiles) -> ExitCodeOrHardError:
        return self.__execute_action()
