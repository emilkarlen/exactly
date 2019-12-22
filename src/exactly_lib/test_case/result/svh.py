from enum import Enum
from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer


class SuccessOrValidationErrorOrHardErrorEnum(Enum):
    SUCCESS = 0
    VALIDATION_ERROR = 1
    HARD_ERROR = 99


class SuccessOrValidationErrorOrHardError(tuple):
    def __new__(cls,
                is_hard_error: Optional[bool],
                failure_message: Optional[TextRenderer],
                ):
        return tuple.__new__(cls, (is_hard_error, failure_message))

    @property
    def status(self) -> SuccessOrValidationErrorOrHardErrorEnum:
        if self.is_success:
            return SuccessOrValidationErrorOrHardErrorEnum.SUCCESS
        if self.is_validation_error:
            return SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR
        return SuccessOrValidationErrorOrHardErrorEnum.HARD_ERROR

    @property
    def is_success(self) -> bool:
        return self[1] is None

    @property
    def failure_message(self) -> Optional[TextRenderer]:
        """
        :return None iff the object represents SUCCESS.
        """
        return self[1]

    @property
    def is_validation_error(self) -> bool:
        return self[0] is False

    @property
    def is_hard_error(self) -> bool:
        return self[0] is True


def new_svh_success() -> SuccessOrValidationErrorOrHardError:
    return __SVH_SUCCESS


def new_svh_validation_error(failure_message: TextRenderer) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A VALIDATION ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(False,
                                               failure_message,
                                               )


def new_svh_validation_error__str(failure_message: str) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A VALIDATION ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(False,
                                               text_docs.single_pre_formatted_line_object(failure_message),
                                               )


def new_maybe_svh_validation_error(failure_message: Optional[TextRenderer]) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        return new_svh_success()
    else:
        return SuccessOrValidationErrorOrHardError(False,
                                                   failure_message,
                                                   )


def new_maybe_svh_validation_error__str(failure_message: Optional[str]) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        return new_svh_success()
    else:
        return SuccessOrValidationErrorOrHardError(False,
                                                   text_docs.single_pre_formatted_line_object(failure_message),
                                                   )


def new_svh_hard_error(failure_message: TextRenderer) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(True,
                                               failure_message,
                                               )


def new_maybe_svh_hard_error(failure_message: Optional[TextRenderer]) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        return new_svh_success()
    return SuccessOrValidationErrorOrHardError(True,
                                               failure_message,
                                               )


def new_svh_hard_error__str(failure_message: str) -> SuccessOrValidationErrorOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrValidationErrorOrHardError(True,
                                               text_docs.single_pre_formatted_line_object(failure_message),
                                               )


__SVH_SUCCESS = SuccessOrValidationErrorOrHardError(None, None)
