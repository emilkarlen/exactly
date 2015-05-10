from .instructions import SuccessOrHardError


__SUCCESS = SuccessOrHardError(None)


def new_success() -> SuccessOrHardError:
    return __SUCCESS


def new_hard_error(failure_message: str) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(failure_message)
