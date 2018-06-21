from typing import Sequence

from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor, \
    ActSourceAndExecutorConstructor, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.execution.test_resources import test_actions
from exactly_lib_test.execution.test_resources.act_source_and_executors import \
    ActSourceAndExecutorThatRunsConstantActions
from exactly_lib_test.test_resources import actions


class ActSourceAndExecutorConstructorThatRunsConstantActions(ActSourceAndExecutorConstructor):
    def __init__(self,
                 parse_action=actions.do_nothing,
                 validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_pre_sds_initial_action=actions.do_nothing,
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_initial_action=actions.do_nothing,
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 prepare_initial_action=actions.do_nothing,
                 execute_action=test_actions.execute_action_that_returns_exit_code(0),
                 execute_initial_action=actions.do_nothing,
                 apply_action_before_executor_is_constructed=actions.do_nothing):
        self.apply_action_before_executor_is_constructed = apply_action_before_executor_is_constructed
        self.parse_action = parse_action
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
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActSourceAndExecutor:
        self.apply_action_before_executor_is_constructed(environment, act_phase_instructions)
        return ActSourceAndExecutorThatRunsConstantActions(
            parse_action=self.parse_action,
            validate_pre_sds_initial_action=self.validate_pre_sds_initial_action,
            validate_pre_sds_action=self.validate_pre_sds_action,
            validate_post_setup_initial_action=self.validate_post_setup_initial_action,
            validate_post_setup_action=self.validate_post_setup_action,
            prepare_initial_action=self.prepare_initial_action,
            prepare_action=self.prepare_action,
            execute_initial_action=self.execute_initial_action,
            execute_action=self.execute_action)


class ActSourceAndExecutorConstructorForConstantExecutor(ActSourceAndExecutorConstructor):
    def __init__(self, executor: ActSourceAndExecutor):
        self.executor = executor

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActSourceAndExecutor:
        return self.executor
