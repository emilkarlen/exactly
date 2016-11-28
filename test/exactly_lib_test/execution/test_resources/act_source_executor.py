import pathlib

from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, ActSourceAndExecutor, \
    ActSourceAndExecutorConstructor, ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources import test_actions


class ActSourceAndExecutorThatRunsConstantActions(ActSourceAndExecutor):
    def __init__(self,
                 validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_pre_sds_initial_action=test_actions.do_nothing,
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_initial_action=test_actions.do_nothing,
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 prepare_initial_action=test_actions.do_nothing,
                 execute_action=test_actions.execute_action_that_returns_exit_code(0),
                 execute_initial_action=test_actions.do_nothing,
                 ):
        self.__validate_pre_sds_initial_action = validate_pre_sds_initial_action
        self.__validate_pre_sds_action = validate_pre_sds_action
        self.__validate_post_setup_initial_action = validate_post_setup_initial_action
        self.__validate_post_setup_action = validate_post_setup_action
        self.__prepare_initial_action = prepare_initial_action
        self.__prepare_action = prepare_action
        self.__execute_initial_action = execute_initial_action
        self.__execute_action = execute_action

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.__validate_pre_sds_initial_action(environment)
        return self.__validate_pre_sds_action(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        self.__validate_post_setup_initial_action(environment)
        return self.__validate_post_setup_action(environment)

    def prepare(self, environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__prepare_initial_action(environment, script_output_dir_path)
        return self.__prepare_action(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__execute_initial_action(environment, script_output_dir_path, std_files)
        return self.__execute_action(environment, script_output_dir_path, std_files)


class ActSourceAndExecutorConstructorThatRunsConstantActions(ActSourceAndExecutorConstructor):
    def __init__(self,
                 validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_pre_sds_initial_action=test_actions.do_nothing,
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_initial_action=test_actions.do_nothing,
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 prepare_initial_action=test_actions.do_nothing,
                 execute_action=test_actions.execute_action_that_returns_exit_code(0),
                 execute_initial_action=test_actions.do_nothing,
                 apply_action_before_executor_is_constructed=test_actions.do_nothing):
        self.apply_action_before_executor_is_constructed = apply_action_before_executor_is_constructed
        self.validate_pre_sds_initial_action = validate_pre_sds_initial_action
        self.validate_pre_sds_action = validate_pre_sds_action
        self.validate_post_setup_initial_action = validate_post_setup_initial_action
        self.validate_post_setup_action = validate_post_setup_action
        self.prepare_initial_action = prepare_initial_action
        self.prepare_action = prepare_action
        self.execute_initial_action = execute_initial_action
        self.execute_action = execute_action

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: list) -> ActSourceAndExecutor:
        self.apply_action_before_executor_is_constructed(environment, act_phase_instructions)
        return ActSourceAndExecutorThatRunsConstantActions(
            validate_pre_sds_initial_action=self.validate_pre_sds_initial_action,
            validate_pre_sds_action=self.validate_pre_sds_action,
            validate_post_setup_initial_action=self.validate_post_setup_initial_action,
            validate_post_setup_action=self.validate_post_setup_action,
            prepare_initial_action=self.prepare_initial_action,
            prepare_action=self.prepare_action,
            execute_initial_action=self.execute_initial_action,
            execute_action=self.execute_action)


def act_phase_handling_that_runs_constant_actions(
        validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
        execute_action=test_actions.execute_action_that_returns_exit_code()) -> ActPhaseHandling:
    return ActPhaseHandling(
        ActSourceAndExecutorConstructorThatRunsConstantActions(
            validate_pre_sds_action=validate_pre_sds_action,
            validate_post_setup_action=validate_post_setup_action,
            prepare_action=prepare_action,
            execute_action=execute_action)
    )
