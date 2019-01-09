from exactly_lib.type_system.error_message import ErrorMessageResolver


class HardErrorException(Exception):
    def __init__(self, error: ErrorMessageResolver):
        self._error = error

    @property
    def error(self) -> ErrorMessageResolver:
        return self._error
