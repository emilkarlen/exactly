from typing import Optional

from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable


class FailureDetails:
    """
    An error message, an exception, or both.
    """

    def __init__(self,
                 failure_message: Optional[FilePrintable],
                 exception: Optional[Exception]):
        self.__failure_message = failure_message
        self.__exception = exception

    @staticmethod
    def new_message(message: FilePrintable,
                    exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(message,
                              exception)

    @staticmethod
    def new_constant_message(message: str,
                             exception: Optional[Exception] = None) -> 'FailureDetails':
        return FailureDetails(file_printables.of_constant_string(message),
                              exception)

    @staticmethod
    def new_exception(exception: Exception,
                      message: Optional[str] = None) -> 'FailureDetails':
        return FailureDetails(None if message is None
                              else file_printables.of_constant_string(message),
                              exception)

    @property
    def is_only_failure_message(self) -> bool:
        return self.__exception is None

    @property
    def failure_message(self) -> FilePrintable:
        return self.__failure_message

    @property
    def has_exception(self) -> Exception:
        return self.__exception is not None

    @property
    def exception(self) -> Exception:
        return self.__exception

    def __str__(self) -> str:
        components = []

        if self.__failure_message is not None:
            components += ['message=' + file_printables.print_to_string(self.__failure_message)]

        if self.__exception is not None:
            components += ['exception=' + str(self.__exception)]

        return '\n\n'.join(components)
