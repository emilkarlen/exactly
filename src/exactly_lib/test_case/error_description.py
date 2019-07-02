from typing import Optional

from exactly_lib.definitions import misc_texts
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib.util.name import Name


class ErrorDescription:
    def __init__(self, message: Optional[FilePrintable]):
        self.__message = message

    @property
    def message(self) -> Optional[FilePrintable]:
        return self.__message


def of_message(message: Optional[FilePrintable]) -> ErrorDescription:
    return ErrorDescriptionOfMessage(message)


def of_constant_message(message: str) -> ErrorDescription:
    return ErrorDescriptionOfMessage(file_printables.of_constant_string(message))


def formatted_error_message_str(category: Name, message: FilePrintable) -> FilePrintable:
    return file_printables.of_sequence(
        [
            file_printables.of_constant_string(category.singular.capitalize() + ': '),
            message,
        ]
    )


def syntax_error_message(message: FilePrintable) -> FilePrintable:
    return formatted_error_message_str(misc_texts.SYNTAX_ERROR_NAME, message)


def file_access_error_message(message: FilePrintable) -> FilePrintable:
    return formatted_error_message_str(misc_texts.FILE_ACCESS_ERROR_NAME,
                                       message)


def syntax_error_of_message(message: FilePrintable) -> ErrorDescription:
    return ErrorDescriptionOfMessage(syntax_error_message(message))


def file_access_error_of_message(message: FilePrintable) -> ErrorDescription:
    return ErrorDescriptionOfMessage(file_access_error_message(message))


def of_exception(exception: Exception,
                 message: Optional[FilePrintable] = None) -> ErrorDescription:
    return ErrorDescriptionOfException(exception, message)


def of_external_process_error(exit_code: int,
                              stderr_output: str,
                              message: Optional[FilePrintable] = None) -> ErrorDescription:
    return ErrorDescriptionOfExternalProcessError(ExternalProcessError(exit_code,
                                                                       stderr_output),
                                                  message)


class ErrorDescriptionOfMessage(ErrorDescription):
    def __init__(self, message: FilePrintable):
        super().__init__(message)


class ErrorDescriptionOfException(ErrorDescription):
    def __init__(self,
                 exception: Exception,
                 message: Optional[FilePrintable] = None):
        super().__init__(message)
        self.__exception = exception

    @property
    def exception(self) -> Exception:
        return self.__exception


class ExternalProcessError(tuple):
    def __new__(cls,
                exit_code: int,
                stderr_output: str):
        return tuple.__new__(cls, (exit_code, stderr_output))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def stderr_output(self) -> str:
        return self[1]


class ErrorDescriptionOfExternalProcessError(ErrorDescription):
    def __init__(self,
                 external_process_error: ExternalProcessError,
                 message: Optional[FilePrintable] = None):
        super().__init__(message)
        self.__external_process_error = external_process_error

    @property
    def external_process_error(self) -> ExternalProcessError:
        return self.__external_process_error


class ErrorDescriptionVisitor:
    def visit(self, error_description: ErrorDescription):
        """
        :return: Return value from _visit... method
        """
        if isinstance(error_description, ErrorDescriptionOfMessage):
            return self._visit_message(error_description)
        elif isinstance(error_description, ErrorDescriptionOfException):
            return self._visit_exception(error_description)
        elif isinstance(error_description, ErrorDescriptionOfExternalProcessError):
            return self._visit_external_process_error(error_description)
        else:
            raise TypeError('Unknown {}: {}'.format(ErrorDescription, str(error_description)))

    def _visit_message(self, error_description: ErrorDescriptionOfMessage):
        raise NotImplementedError()

    def _visit_exception(self, error_description: ErrorDescriptionOfException):
        raise NotImplementedError()

    def _visit_external_process_error(self, error_description: ErrorDescriptionOfExternalProcessError):
        raise NotImplementedError()
