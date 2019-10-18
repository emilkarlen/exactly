from typing import Optional, TypeVar, Generic

from exactly_lib.common.err_msg.msg import minors
from exactly_lib.common.report_rendering.text_doc import MinorTextRenderer
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import line_objects, blocks
from exactly_lib.util.simple_textstruct.structure import LineElement


class ErrorDescription:
    def __init__(self, message: Optional[MinorTextRenderer]):
        self.__message = message

    @property
    def message(self) -> Optional[MinorTextRenderer]:
        return self.__message


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


def of_message(message: Optional[MinorTextRenderer]) -> ErrorDescription:
    return ErrorDescriptionOfMessage(message)


def of_constant_message(message: str) -> ErrorDescription:
    return ErrorDescriptionOfMessage(
        blocks.MinorBlocksOfSingleLineObject(line_objects.PreFormattedString(message))
    )


def syntax_error_of_message(message: SequenceRenderer[LineElement]) -> ErrorDescription:
    return ErrorDescriptionOfMessage(minors.syntax_error_message(message))


def file_access_error_of_message(message: SequenceRenderer[LineElement]) -> ErrorDescription:
    return ErrorDescriptionOfMessage(minors.file_access_error_message(message))


def of_exception(exception: Exception,
                 message: Optional[MinorTextRenderer] = None) -> ErrorDescription:
    return ErrorDescriptionOfException(exception, message)


def of_external_process_error(exit_code: int,
                              stderr_output: str,
                              message: Optional[MinorTextRenderer] = None) -> ErrorDescription:
    return ErrorDescriptionOfExternalProcessError(ExternalProcessError(exit_code,
                                                                       stderr_output),
                                                  message)


def of_external_process_error2(process_error: ExternalProcessError,
                               message: Optional[MinorTextRenderer] = None) -> ErrorDescription:
    return ErrorDescriptionOfExternalProcessError(process_error,
                                                  message)


class ErrorDescriptionOfMessage(ErrorDescription):
    def __init__(self, message: MinorTextRenderer):
        super().__init__(message)


class ErrorDescriptionOfException(ErrorDescription):
    def __init__(self,
                 exception: Exception,
                 message: Optional[MinorTextRenderer] = None):
        super().__init__(message)
        self.__exception = exception

    @property
    def exception(self) -> Exception:
        return self.__exception


class ErrorDescriptionOfExternalProcessError(ErrorDescription):
    def __init__(self,
                 external_process_error: ExternalProcessError,
                 message: Optional[MinorTextRenderer] = None):
        super().__init__(message)
        self.__external_process_error = external_process_error

    @property
    def external_process_error(self) -> ExternalProcessError:
        return self.__external_process_error


RET = TypeVar('RET')


class ErrorDescriptionVisitor(Generic[RET]):
    def visit(self, error_description: ErrorDescription) -> RET:
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

    def _visit_message(self, error_description: ErrorDescriptionOfMessage) -> RET:
        raise NotImplementedError()

    def _visit_exception(self, error_description: ErrorDescriptionOfException) -> RET:
        raise NotImplementedError()

    def _visit_external_process_error(self, error_description: ErrorDescriptionOfExternalProcessError) -> RET:
        raise NotImplementedError()
