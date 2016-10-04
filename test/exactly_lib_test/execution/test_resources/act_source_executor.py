import pathlib

from exactly_lib.execution.act_phase import SourceSetup, ActSourceExecutor, ExitCodeOrHardError, ActSourceAndExecutor
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.test_case.phases.act.program_source import ActSourceBuilder
from exactly_lib.test_case.phases.common import HomeAndEds
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources import test_actions


class ActSourceExecutorThatRunsConstantActions(ActSourceExecutor):
    def __init__(self,
                 validate_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 execute_action=test_actions.execute_action_that_returns_exit_code()):
        self.__validate_action = validate_action
        self.__prepare_action = prepare_action
        self.__execute_action = execute_action

    def validate(self,
                 home_dir: pathlib.Path(),
                 source: ActSourceBuilder) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_action()

    def prepare(self,
                source_setup: SourceSetup,
                home_dir_path: pathlib.Path,
                eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        return self.__prepare_action()

    def execute(self,
                source_setup: SourceSetup,
                home_dir: pathlib.Path,
                eds: ExecutionDirectoryStructure,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.__execute_action()


class ActSourceAndExecutorThatRunsConstantActions(ActSourceAndExecutor):
    def __init__(self,
                 validate_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 execute_action=test_actions.execute_action_that_returns_exit_code()):
        self.__validate_action = validate_action
        self.__prepare_action = prepare_action
        self.__execute_action = execute_action

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_action()

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self.__prepare_action()

    def execute(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.__execute_action()
