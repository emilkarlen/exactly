from shelltest.test_case.instructions import PassOrFailOrHardError, PassOrFailOrHardErrorEnum


def new_success() -> PassOrFailOrHardError:
    return __SUCCESS


def new_fail(message: str) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 message)


def new_hard_error(message: str) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 message)


__SUCCESS = PassOrFailOrHardError(PassOrFailOrHardErrorEnum.PASS,
                                  None)
