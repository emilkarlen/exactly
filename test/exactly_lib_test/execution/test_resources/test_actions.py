from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.failure_details import new_failure_details_from_message


def do_nothing(*args, **kwargs):
    pass


def validate_action_that_returns(ret_val: svh.SuccessOrValidationErrorOrHardError):
    def f():
        return ret_val

    return f


def prepare_action_that_returns(ret_val: sh.SuccessOrHardError):
    def f():
        return ret_val

    return f


def validate_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f


def execute_action_that_returns_exit_code(exit_code: int = 0):
    def f() -> ExitCodeOrHardError:
        return new_eh_exit_code(exit_code)

    return f


def prepare_action_that_returns_hard_error_with_message(message: str):
    def f() -> sh.SuccessOrHardError:
        # return sh.new_sh_hard_error(new_failure_details_from_message(message))
        return sh.new_sh_hard_error(message)

    return f


def execute_action_that_returns_hard_error_with_message(message: str):
    def f() -> ExitCodeOrHardError:
        return new_eh_hard_error(new_failure_details_from_message(message))

    return f


def execute_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f
