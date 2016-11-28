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


class Command(tuple):
    def __new__(cls,
                args,
                shell: bool):
        return tuple.__new__(cls, (args, shell))

    @property
    def args(self):
        """
        :return: Either a string or an iterable of strings
        """
        return self[0]

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        return self[1]
