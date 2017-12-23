from exactly_lib.help_texts import misc_texts


class ErrorDescription:
    def __init__(self,
                 message: str):
        self.__message = message

    @property
    def message(self) -> str:
        return self.__message


def of_message(message: str) -> ErrorDescription:
    return ErrorDescriptionOfMessage(message)


def syntax_error_message(message: str) -> str:
    return (misc_texts.SYNTAX_ERROR_NAME.singular.capitalize() +
            ': ' +
            message)


def syntax_error_of_message(message: str) -> ErrorDescription:
    return ErrorDescriptionOfMessage(syntax_error_message(message))


def of_exception(exception: Exception,
                 message: str = None) -> ErrorDescription:
    return ErrorDescriptionOfException(exception, message)


def of_external_process_error(exit_code: int,
                              stderr_output: str,
                              message: str = None) -> ErrorDescription:
    return ErrorDescriptionOfExternalProcessError(ExternalProcessError(exit_code,
                                                                       stderr_output),
                                                  message)


class ErrorDescriptionOfMessage(ErrorDescription):
    def __init__(self, message: str):
        super().__init__(message)


class ErrorDescriptionOfException(ErrorDescription):
    def __init__(self,
                 exception: Exception,
                 message: str = None):
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
                 message: str = None):
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
