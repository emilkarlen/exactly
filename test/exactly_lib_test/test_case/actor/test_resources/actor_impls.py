from typing import Sequence

from exactly_lib.test_case.phases.act.actor import ActionToCheck, Actor, ParseException
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.result import sh, svh
from exactly_lib_test.test_case.actor.test_resources import test_actions
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.execute_methods import BeforeExecuteMethod
from exactly_lib_test.test_resources import actions


class ActorThatRunsConstantActions(Actor):
    def __init__(self,
                 parse_atc=actions.do_nothing,
                 validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_pre_sds_initial_action=actions.do_nothing,
                 validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
                 validate_post_setup_initial_action=actions.do_nothing,
                 prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
                 prepare_initial_action=actions.do_nothing,
                 execute_action=test_actions.execute_action_that_returns_exit_code(0),
                 execute_initial_action: BeforeExecuteMethod = actions.do_nothing,
                 apply_action_before_atc_is_constructed=actions.do_nothing):
        self.apply_action_before_atc_is_constructed = apply_action_before_atc_is_constructed
        self.parse_atc = parse_atc
        self.validate_pre_sds_initial_action = validate_pre_sds_initial_action
        self.validate_pre_sds_action = validate_pre_sds_action
        self.validate_post_setup_initial_action = validate_post_setup_initial_action
        self.validate_post_setup_action = validate_post_setup_action
        self.prepare_initial_action = prepare_initial_action
        self.prepare_action = prepare_action
        self.execute_initial_action = execute_initial_action
        self.execute_action = execute_action

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        self.apply_action_before_atc_is_constructed(instructions)
        self.parse_atc(instructions)
        return ActionToCheckThatRunsConstantActions(
            validate_pre_sds_initial_action=self.validate_pre_sds_initial_action,
            validate_pre_sds_action=self.validate_pre_sds_action,
            validate_post_setup_initial_action=self.validate_post_setup_initial_action,
            validate_post_setup_action=self.validate_post_setup_action,
            prepare_initial_action=self.prepare_initial_action,
            prepare_action=self.prepare_action,
            execute_initial_action=self.execute_initial_action,
            execute_action=self.execute_action)


class ActorForConstantAtc(Actor):
    def __init__(self,
                 atc: ActionToCheck,
                 parse_atc=actions.do_nothing,
                 ):
        self.atc = atc
        self.parse_atc = parse_atc

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        self.parse_atc(instructions)
        return self.atc


class ActorThatRaisesImplementationException(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]):
        raise ValueError('the method should never be called')


class ActorThatRaisesParseException(Actor):
    def parse(self, instructions: Sequence[ActPhaseInstruction]):
        raise ParseException.of_str('unconditional parse failure')
