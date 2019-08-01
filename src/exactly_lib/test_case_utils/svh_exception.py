from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.result import svh
from exactly_lib.util.file_printer import FilePrintable


class SvhException(Exception):
    def __init__(self,
                 err_msg: FilePrintable,
                 err_msg__td: TextRenderer,
                 ):
        super().__init__()
        self._err_msg = err_msg
        self._err_msg__td = err_msg__td

    @property
    def err_msg(self) -> FilePrintable:
        return self._err_msg

    @property
    def err_msg__td(self) -> TextRenderer:
        return self._err_msg__td


class SvhValidationException(SvhException):
    def __init__(self, err_msg: FilePrintable):
        super().__init__(err_msg,
                         text_docs.single_pre_formatted_line_object__from_fp(err_msg),
                         )


class SvhHardErrorException(SvhException):
    def __init__(self, err_msg: FilePrintable):
        super().__init__(err_msg,
                         text_docs.single_pre_formatted_line_object__from_fp(err_msg),
                         )


def translate_svh_exception_to_svh(action,
                                   *args, **kwargs) -> svh.SuccessOrValidationErrorOrHardError:
    try:
        action(*args, **kwargs)
        return svh.new_svh_success()

    except SvhValidationException as ex:
        return svh.new_svh_validation_error(ex.err_msg)

    except SvhHardErrorException as ex:
        return svh.new_svh_hard_error(ex.err_msg)
