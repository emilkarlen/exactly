from typing import Callable, TypeVar


def do_nothing(*args, **kwargs):
    pass


def do_nothing__single_arg(args):
    pass


def do_return(x) -> Callable:
    def ret_val(*args, **kwargs):
        return x

    return ret_val


T = TypeVar('T')


def do_return__wo_args(x: T) -> Callable[[], T]:
    def ret_val() -> T:
        return x

    return ret_val


def do_raise(ex: Exception) -> Callable:
    def ret_val(*args, **kwargs):
        raise ex

    return ret_val


def action_of(initial_action: Callable, action_that_returns: Callable) -> Callable:
    if initial_action:
        def complete_action(*args, **kwargs):
            initial_action(*args, **kwargs)
            return action_that_returns(*args, **kwargs)

        return complete_action
    else:
        return action_that_returns
