from enum import Enum


class PassOrFailOrHardErrorEnum(Enum):
    """
    Implementation note: The error-values must correspond to those of PartialControlledFailureEnum
    """
    PASS = 0
    FAIL = 2
    HARD_ERROR = 99


class PassOrFailOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                status: PassOrFailOrHardErrorEnum,
                failure_message: str):
        return tuple.__new__(cls, (status, failure_message,))

    @property
    def status(self) -> PassOrFailOrHardErrorEnum:
        return self[0]

    @property
    def is_error(self) -> bool:
        return self.status is not PassOrFailOrHardErrorEnum.PASS

    @property
    def failure_message(self) -> str:
        """
        :return None iff the object represents PASS.
        """
        return self[1]


__PFH_PASS = PassOrFailOrHardError(PassOrFailOrHardErrorEnum.PASS, None)


def new_pfh_pass() -> PassOrFailOrHardError:
    return __PFH_PASS


def new_pfh_fail(failure_message: str) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 failure_message)


def new_pfh_fail_if_has_failure_message(failure_message: str) -> PassOrFailOrHardError:
    return new_pfh_fail(failure_message) if failure_message else new_pfh_pass()


def new_pfh_hard_error(failure_message: str) -> PassOrFailOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 failure_message)
