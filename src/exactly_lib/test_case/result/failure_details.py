from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable


class FailureDetails:
    """
    An error message, an exception, or both.
    """

    def __init__(self,
                 failure_message: Optional[FilePrintable],
                 failure_message_td: Optional[TextRenderer],
                 exception: Optional[Exception]):
        self.__failure_message_fp = failure_message
        self.__failure_message_td = failure_message_td
        self.__exception = exception

    @staticmethod
    def new_message(message: FilePrintable,
                    exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(message,
                              text_docs.single_pre_formatted_line_object__from_fp(message),
                              exception)

    @staticmethod
    def new_message__td(message: TextRenderer,
                        exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(text_docs.as_file_printable(message),
                              message,
                              exception)

    @staticmethod
    def new_constant_message(message: str,
                             exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(file_printables.of_string(message),
                              text_docs.single_pre_formatted_line_object(message),
                              exception)

    @staticmethod
    def new_exception(exception: Exception,
                      message: Optional[str] = None) -> 'FailureDetails':
        if message is None:
            return FailureDetails(None,
                                  None,
                                  exception)
        else:
            return FailureDetails(file_printables.of_string(message),
                                  text_docs.single_pre_formatted_line_object(message),
                                  exception)

    @property
    def is_only_failure_message(self) -> bool:
        return self.__exception is None

    @property
    def failure_message(self) -> Optional[FilePrintable]:
        return self.__failure_message_fp

    @property
    def failure_message__as_text_doc(self) -> Optional[TextRenderer]:
        return self.__failure_message_td

    @property
    def has_exception(self) -> bool:
        return self.__exception is not None

    @property
    def exception(self) -> Exception:
        return self.__exception

    def __str__(self) -> str:
        components = []

        if self.__failure_message_fp is not None:
            components += ['message=' + file_printables.print_to_string(self.__failure_message_fp)]

        if self.__exception is not None:
            components += ['exception=' + str(self.__exception)]

        return '\n\n'.join(components)
