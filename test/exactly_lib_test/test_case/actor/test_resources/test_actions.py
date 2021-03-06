from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.result.failure_details import FailureDetails


def validate_action_that_returns(ret_val: svh.SuccessOrValidationErrorOrHardError):
    def f(*args, **kwargs):
        return ret_val

    return f


def prepare_action_that_returns(ret_val: sh.SuccessOrHardError):
    def f(*args, **kwargs):
        return ret_val

    return f


def validate_action_that_raises(ex: Exception):
    def f(*args, **kwargs):
        raise ex

    return f


def execute_action_that_returns_exit_code(exit_code: int = 0):
    def f(*args, **kwargs) -> ExitCodeOrHardError:
        return new_eh_exit_code(exit_code)

    return f


def prepare_action_that_returns_hard_error_with_message(message: str):
    def f(*args, **kwargs) -> sh.SuccessOrHardError:
        return sh.new_sh_hard_error__str(message)

    return f


def prepare_action_that_raises(ex: Exception):
    def f(*args, **kwargs) -> sh.SuccessOrHardError:
        raise ex

    return f


def execute_action_that_returns_hard_error_with_message(message: str):
    def f(*args, **kwargs) -> ExitCodeOrHardError:
        return new_eh_hard_error(FailureDetails.new_constant_message(message))

    return f


def execute_action_that_raises(ex: Exception):
    def f(*args, **kwargs):
        raise ex

    return f
