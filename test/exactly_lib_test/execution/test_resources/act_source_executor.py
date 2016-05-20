import pathlib

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.phase_setup import ActSourceExecutor, SourceSetup
from exactly_lib.test_case.phases.act.script_source import ActSourceBuilder
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles


class ActSourceExecutorThatRunsConstantActions(ActSourceExecutor):
    def __init__(self,
                 validate_test_action,
                 execute_test_action):
        self.__validate_test_action = validate_test_action
        self.__execute_test_action = execute_test_action

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_test_action()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure):
        pass

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> int:
        return self.__execute_test_action()
