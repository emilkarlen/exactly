from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import svh


class SvhException(Exception):
    def __init__(self,
                 err_msg: TextRenderer,
                 ):
        super().__init__()
        self._err_msg = err_msg

    @property
    def err_msg(self) -> TextRenderer:
        return self._err_msg


class SvhValidationException(SvhException):
    pass


class SvhHardErrorException(SvhException):
    pass


def translate_svh_exception_to_svh(action,
                                   *args, **kwargs) -> svh.SuccessOrValidationErrorOrHardError:
    try:
        action(*args, **kwargs)
        return svh.new_svh_success()

    except SvhValidationException as ex:
        return svh.new_svh_validation_error(ex.err_msg)

    except SvhHardErrorException as ex:
        return svh.new_svh_hard_error(ex.err_msg)
