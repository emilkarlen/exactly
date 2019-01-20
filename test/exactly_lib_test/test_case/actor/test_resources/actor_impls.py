from typing import Sequence

from exactly_lib.test_case.actor import ActionToCheckExecutor, Actor, ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.test_case.actor.test_resources import test_actions
from exactly_lib_test.test_case.actor.test_resources.act_source_and_executors import \
    ActionToCheckExecutorThatRunsConstantActions
from exactly_lib_test.test_resources import actions


class ActorThatRunsConstantActions(Actor):
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

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheckExecutor:
        self.apply_action_before_executor_is_constructed(instructions)
        self.parse_action(instructions)
        return ActionToCheckExecutorThatRunsConstantActions(
            validate_pre_sds_initial_action=self.validate_pre_sds_initial_action,
            validate_pre_sds_action=self.validate_pre_sds_action,
            validate_post_setup_initial_action=self.validate_post_setup_initial_action,
            validate_post_setup_action=self.validate_post_setup_action,
            prepare_initial_action=self.prepare_initial_action,
            prepare_action=self.prepare_action,
            execute_initial_action=self.execute_initial_action,
            execute_action=self.execute_action)


class ActorForConstantExecutor(Actor):
    def __init__(self,
                 executor: ActionToCheckExecutor,
                 parse_action=actions.do_nothing,
                 ):
        self.executor = executor
        self.parse_action = parse_action

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheckExecutor:
        self.parse_action(instructions)
        return self.executor


class ActorThatRaisesImplementationException(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]):
        raise ValueError('the method should never be called')


class ActorThatRaisesParseException(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]):
        raise ParseException(svh.new_svh_validation_error('unconditional parse failure'))
