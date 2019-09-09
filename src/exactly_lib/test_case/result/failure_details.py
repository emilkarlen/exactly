from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer


class FailureDetails:
    """
    An error message, an exception, or both.
    """

    def __init__(self,
                 failure_message: Optional[TextRenderer],
                 exception: Optional[Exception]):
        self.__failure_message = failure_message
        self.__exception = exception

    @staticmethod
    def new_message(message: TextRenderer,
                    exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(message,
                              exception)

    @staticmethod
    def new_constant_message(message: str,
                             exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(text_docs.single_pre_formatted_line_object(message),
                              exception)

    @staticmethod
    def new_exception(exception: Exception,
                      message: Optional[str] = None) -> 'FailureDetails':
        if message is None:
            return FailureDetails(None,
                                  exception)
        else:
            return FailureDetails(text_docs.single_pre_formatted_line_object(message),
                                  exception)

    @property
    def is_only_failure_message(self) -> bool:
        return self.__exception is None

    @property
    def failure_message(self) -> Optional[TextRenderer]:
        return self.__failure_message

    @property
    def has_exception(self) -> bool:
        return self.__exception is not None

    @property
    def exception(self) -> Exception:
        return self.__exception

    def __str__(self) -> str:
        from exactly_lib.util.simple_textstruct.file_printer_output import to_string

        components = []

        if self.__failure_message is not None:
            components += ['message=' + to_string.major_blocks(self.__failure_message.render_sequence())]

        if self.__exception is not None:
            components += ['exception=' + str(self.__exception)]

        return '\n\n'.join(components)
