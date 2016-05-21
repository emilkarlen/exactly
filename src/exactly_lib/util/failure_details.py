class FailureDetails:
    """
    An error message, an exception, or both.
    """

    def __init__(self,
                 failure_message: str,
                 exception: Exception):
        self.__failure_message = failure_message
        self.__exception = exception

    @property
    def is_only_failure_message(self) -> bool:
        return self.__exception is None

    @property
    def failure_message(self) -> str:
        return self.__failure_message

    @property
    def has_exception(self) -> Exception:
        return self.__exception is not None

    @property
    def exception(self) -> Exception:
        return self.__exception

    def __str__(self) -> str:
        if self.is_only_failure_message:
            return self.__failure_message
        else:
            return str(self.exception)


def new_failure_details_from_exception(exception: Exception,
                                       message: str = None) -> FailureDetails:
    return FailureDetails(message, exception)


def new_failure_details_from_message(error_message: str) -> FailureDetails:
    return FailureDetails(error_message, None)
