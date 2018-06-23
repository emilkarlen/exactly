from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.result import svh, sh
from exactly_lib_test.test_case.act_phase_handling.test_resources import test_actions
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActSourceAndExecutorConstructorThatRunsConstantActions, ActSourceAndExecutorConstructorThatRaisesException


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


def dummy_act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRunsConstantActions())


def act_phase_handling_that_must_not_be_used() -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRaisesException())
