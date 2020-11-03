from typing import Callable

from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.result import sh


def return_success_or_hard_error(procedure: Callable, *args, **kwargs) -> sh.SuccessOrHardError:
    """
    Executes a callable (by invoking its __call__), and returns hard-error iff
    a `HardErrorException` is raised, otherwise success.
    :param procedure:
    :param args: Arguments given to callable_block
    :param kwargs: Arguments given to callable_block
    :return: success iff callable_block does not raise `HardErrorException`, otherwise success
    """
    try:
        procedure(*args, **kwargs)
        return sh.new_sh_success()
    except HardErrorException as ex:
        return sh.new_sh_hard_error(ex.error)
