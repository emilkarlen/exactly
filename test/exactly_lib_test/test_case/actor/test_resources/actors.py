from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.result import svh, sh
from exactly_lib_test.test_case.actor.test_resources import test_actions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import \
    ActorThatRunsConstantActions, ActorThatRaisesImplementationException


def actor_that_runs_constant_actions(
        validate_pre_sds_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        validate_post_setup_action=test_actions.validate_action_that_returns(svh.new_svh_success()),
        prepare_action=test_actions.prepare_action_that_returns(sh.new_sh_success()),
        execute_action=test_actions.execute_action_that_returns_exit_code()) -> Actor:
    return ActorThatRunsConstantActions(
        validate_pre_sds_action=validate_pre_sds_action,
        validate_post_setup_action=validate_post_setup_action,
        prepare_action=prepare_action,
        execute_action=execute_action
    )


def dummy_actor() -> Actor:
    return ActorThatRunsConstantActions()


def actor_that_must_not_be_used() -> Actor:
    return ActorThatRaisesImplementationException()
