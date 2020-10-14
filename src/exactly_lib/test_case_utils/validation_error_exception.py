from exactly_lib.common.report_rendering.text_doc import TextRenderer


class ValidationErrorException(Exception):
    def __init__(self, error: TextRenderer):
        self._error = error

    @property
    def error(self) -> TextRenderer:
        return self._error
