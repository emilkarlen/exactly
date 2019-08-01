from enum import Enum
from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
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
                failure_message: Optional[FilePrintable],
                failure_message_td: Optional[TextRenderer],
                ):
        return tuple.__new__(cls, (status, failure_message, failure_message_td))

    @property
    def status(self) -> PassOrFailOrHardErrorEnum:
        return self[0]

    @property
    def is_error(self) -> bool:
        return self.status is not PassOrFailOrHardErrorEnum.PASS

    @property
    def failure_message(self) -> Optional[FilePrintable]:
        """
        :return None iff the object represents PASS.
        """
        return self[1]

    @property
    def failure_message__td(self) -> Optional[TextRenderer]:
        """
        :return None iff the object represents PASS.
        """
        return self[2]


__PFH_PASS = PassOrFailOrHardError(PassOrFailOrHardErrorEnum.PASS, None, None)


def new_pfh_pass() -> PassOrFailOrHardError:
    return __PFH_PASS


def new_pfh_non_pass(status: PassOrFailOrHardErrorEnum,
                     failure_message: FilePrintable) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(status,
                                 failure_message,
                                 text_docs.single_pre_formatted_line_object__from_fp(failure_message),
                                 )


def new_pfh_fail(failure_message: FilePrintable) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 failure_message,
                                 text_docs.single_pre_formatted_line_object__from_fp(failure_message),
                                 )


def new_pfh_fail__td(failure_message: TextRenderer) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.FAIL,
                                 text_docs.as_file_printable(failure_message),
                                 failure_message,
                                 )


def new_pfh_fail__str(failure_message: str) -> PassOrFailOrHardError:
    return new_pfh_fail(file_printables.of_string(failure_message))


def new_pfh_fail_if_has_failure_message(failure_message: Optional[FilePrintable]) -> PassOrFailOrHardError:
    return (
        new_pfh_pass()
        if failure_message is None
        else new_pfh_fail(failure_message)
    )


def new_pfh_fail_if_has_failure_message__str(failure_message: Optional[str]) -> PassOrFailOrHardError:
    return (
        new_pfh_pass()
        if failure_message is None
        else new_pfh_fail(file_printables.of_string(failure_message))
    )


def new_pfh_fail_if_has_failure_message__td(failure_message: Optional[TextRenderer]) -> PassOrFailOrHardError:
    return (
        new_pfh_pass()
        if failure_message is None
        else new_pfh_fail__td(failure_message)
    )


def new_pfh_hard_error(failure_message: FilePrintable) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 failure_message,
                                 text_docs.single_pre_formatted_line_object__from_fp(failure_message),
                                 )


def new_pfh_hard_error__td(failure_message: TextRenderer) -> PassOrFailOrHardError:
    return PassOrFailOrHardError(PassOrFailOrHardErrorEnum.HARD_ERROR,
                                 text_docs.as_file_printable(failure_message),
                                 failure_message,
                                 )


def new_pfh_hard_error__str(failure_message: str) -> PassOrFailOrHardError:
    return new_pfh_hard_error(file_printables.of_string(failure_message))
