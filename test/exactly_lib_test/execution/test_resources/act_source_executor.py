import pathlib

from exactly_lib.execution.act_phase import ExitCodeOrHardError, ActSourceAndExecutor, \
    ActSourceAndExecutorConstructor, ActPhaseHandling
from exactly_lib.test_case.phases.common import HomeAndEds, InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources import test_actions


class ActSourceAndExecutorThatRunsConstantActions(ActSourceAndExecutor):
    def __init__(self,
                 validate_pre_eds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 execute_action=test_actions.execute_action_that_returns_exit_code()):
        self.__validate_pre_eds_action = validate_pre_eds_action
        self.__validate_post_setup_action = validate_post_setup_action
        self.__prepare_action = prepare_action
        self.__execute_action = execute_action

    def validate_pre_sds(self, home_dir_path: pathlib.Path) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_pre_eds_action()

    def validate_post_setup(self, home_and_eds: HomeAndEds) -> svh.SuccessOrValidationErrorOrHardError:
        return self.__validate_post_setup_action()

    def prepare(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self.__prepare_action()

    def execute(self, home_and_eds: HomeAndEds, script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        return self.__execute_action()


class ActSourceAndExecutorConstructorThatRunsConstantActions(ActSourceAndExecutorConstructor):
    def __init__(self,
                 validate_pre_eds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 execute_action=test_actions.execute_action_that_returns_exit_code(),
                 apply_action_before_executor_is_constructed=test_actions.do_nothing):
        self.apply_action_before_executor_is_constructed = apply_action_before_executor_is_constructed
        self.validate_pre_eds_action = validate_pre_eds_action
        self.validate_post_setup_action = validate_post_setup_action
        self.prepare_action = prepare_action
        self.execute_action = execute_action

    def apply(self,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        self.apply_action_before_executor_is_constructed(environment, act_phase_instructions)
        return ActSourceAndExecutorThatRunsConstantActions(
            validate_pre_eds_action=self.validate_pre_eds_action,
            validate_post_setup_action=self.validate_post_setup_action,
            prepare_action=self.prepare_action,
            execute_action=self.execute_action)


def act_phase_handling_that_runs_constant_actions(
        validate_pre_eds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
        execute_action=test_actions.execute_action_that_returns_exit_code()) -> ActPhaseHandling:
    return ActPhaseHandling(
        ActSourceAndExecutorConstructorThatRunsConstantActions(
            validate_pre_eds_action=validate_pre_eds_action,
            validate_post_setup_action=validate_post_setup_action,
            prepare_action=prepare_action,
            execute_action=execute_action)
    )
