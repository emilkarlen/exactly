from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import pfh


class PfhException(Exception):
    """
    An exception that represents a
    :class:`pfh.PassOrFailOrHardError` value
    that is not :class:`pfh.PassOrFailOrHardErrorEnum.PASS`.
    """

    def __init__(self,
                 status: pfh.PassOrFailOrHardErrorEnum,
                 err_msg: TextRenderer,
                 ):
        super().__init__(err_msg)
        self._status = status
        self._err_msg = err_msg

    @property
    def pfh(self) -> pfh.PassOrFailOrHardError:
        return pfh.PassOrFailOrHardError(self._status,
                                         self._err_msg)

    @property
    def err_msg(self) -> TextRenderer:
        return self._err_msg


class PfhFailException(PfhException):
    def __init__(self,
                 err_msg: TextRenderer,
                 ):
        super().__init__(pfh.PassOrFailOrHardErrorEnum.FAIL,
                         err_msg)


class PfhHardErrorException(PfhException):
    def __init__(self,
                 err_msg: TextRenderer,
                 ):
        super().__init__(pfh.PassOrFailOrHardErrorEnum.HARD_ERROR,
                         err_msg)


def translate_pfh_exception_to_pfh(action,
                                   *args, **kwargs) -> pfh.PassOrFailOrHardError:
    try:
        action(*args, **kwargs)
        return pfh.new_pfh_pass()

    except PfhException as ex:
        return ex.pfh
