from .instructions import SuccessOrValidationErrorOrHardError


__SUCCESS = SuccessOrValidationErrorOrHardError(None, None)


def new_success() -> SuccessOrValidationErrorOrHardError:
    return __SUCCESS


def new_validation_error(failure_message: str) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A VALIDATION ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(False, failure_message)


def new_hard_error(failure_message: str) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(True, failure_message)
