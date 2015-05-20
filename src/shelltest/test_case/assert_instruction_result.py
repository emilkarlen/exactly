from .instructions import PassOrFailOrHardErrorEnum, PassOrFailOrHardError


__PASS = PassOrFailOrHardError(PassOrFailOrHardErrorEnum.PASS,
                               None)


def new_pass() -> PassOrFailOrHardError:
    return __PASS


def new_fail(error_message: str) -> PassOrFailOrHardError:
    if error_message is None:
        raise ValueError('A FAIL must have an error message')
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 error_message)


def new_hard_error(error_message: str) -> PassOrFailOrHardError:
    if error_message is None:
        raise ValueError('A HARD ERROR must have an error message')
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 error_message)
