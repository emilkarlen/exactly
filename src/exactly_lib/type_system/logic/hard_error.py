from exactly_lib.test_case_utils.err_msg2.env_dep_text import TextResolver


class HardErrorException(Exception):
    def __init__(self, error: TextResolver):
        self._error = error

    @property
    def error(self) -> TextResolver:
        return self._error
