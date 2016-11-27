class ProcessExecutionSettings(tuple):
    def __new__(cls,
                timeout_in_seconds: int = None,
                environ: dict = None):
        return tuple.__new__(cls, (timeout_in_seconds, environ))

    @property
    def timeout_in_seconds(self) -> int:
        """
        :return: None if no timeout
        """
        return self[0]

    @property
    def environ(self) -> dict:
        """
        :return: None if inherit current process' environment
        """
        return self[1]


def with_no_timeout() -> ProcessExecutionSettings:
    return ProcessExecutionSettings()
