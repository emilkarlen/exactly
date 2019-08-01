from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable


class SuccessOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                failure_message: Optional[FilePrintable],
                failure_message_td: Optional[TextRenderer],
                ):
        return tuple.__new__(cls, (failure_message, failure_message_td))

    @property
    def failure_message(self) -> Optional[FilePrintable]:
        return self[0]

    @property
    def failure_message__as_td(self) -> Optional[TextRenderer]:
        return self[1]

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
    return SuccessOrHardError(failure_message,
                              text_docs.single_pre_formatted_line_object__from_fp(failure_message),
                              )


def new_sh_hard_error__str(failure_message: str) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(file_printables.of_string(failure_message),
                              text_docs.single_pre_formatted_line_object(failure_message),
                              )


def new_sh_hard_error__td(failure_message: TextRenderer) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(text_docs.as_file_printable(failure_message),
                              failure_message,
                              )


__SH_SUCCESS = SuccessOrHardError(None, None)
