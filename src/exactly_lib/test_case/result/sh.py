from typing import Optional

from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable


class SuccessOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                failure_message: Optional[FilePrintable]):
        return tuple.__new__(cls, (failure_message,))

    @property
    def failure_message(self) -> FilePrintable:
        """
        :raises ValueError: iff the object does not represent SUCCESS
        """
        return self[0]

    @property
    def is_success(self) -> bool:
        return self[0] is None

    @property
    def is_hard_error(self) -> bool:
        return not self.is_success

    def __str__(self):
        if self.is_success:
            return 'SUCCESS'
        else:
            return 'FAILURE:' + file_printables.print_to_string(self.failure_message)


def new_sh_success() -> SuccessOrHardError:
    return __SH_SUCCESS


def new_sh_hard_error(failure_message: FilePrintable) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(failure_message)


def new_sh_hard_error__const(failure_message: str) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(file_printables.of_constant_string(failure_message))


__SH_SUCCESS = SuccessOrHardError(None)
