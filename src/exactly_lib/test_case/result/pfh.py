from enum import Enum
from typing import Optional

from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable


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
                failure_message: Optional[FilePrintable]):
        # DEBUG - begin
        if failure_message is not None:
            if not isinstance(failure_message, FilePrintable):
                raise ValueError('Not a FilePrintable: ' + str(failure_message))
        # DEBUG - end
        return tuple.__new__(cls, (status, failure_message,))

    @property
    def status(self) -> PassOrFailOrHardErrorEnum:
        return self[0]

    @property
    def is_error(self) -> bool:
        return self.status is not PassOrFailOrHardErrorEnum.PASS

    @property
    def failure_message_printable(self) -> Optional[FilePrintable]:
        """
        :return None iff the object represents PASS.
        """
        return self[1]


__PFH_PASS = PassOrFailOrHardError(PassOrFailOrHardErrorEnum.PASS, None)


def new_pfh_pass() -> PassOrFailOrHardError:
    return __PFH_PASS


def new_pfh_fail(failure_message: FilePrintable) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 failure_message)


def new_pfh_fail__const(failure_message: str) -> PassOrFailOrHardError:
    return new_pfh_fail(file_printables.of_constant_string(failure_message))


def new_pfh_fail_if_has_failure_message(failure_message: Optional[FilePrintable]) -> PassOrFailOrHardError:
    return (
        new_pfh_pass()
        if failure_message is None
        else new_pfh_fail(failure_message)
    )


def new_pfh_fail_if_has_failure_message__const(failure_message: Optional[str]) -> PassOrFailOrHardError:
    return (
        new_pfh_pass()
        if failure_message is None
        else new_pfh_fail(file_printables.of_constant_string(failure_message))
    )


def new_pfh_hard_error(failure_message: FilePrintable) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 failure_message)


def new_pfh_hard_error__const(failure_message: str) -> PassOrFailOrHardError:
    return new_pfh_hard_error(file_printables.of_constant_string(failure_message))
