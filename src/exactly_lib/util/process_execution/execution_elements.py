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


def with_environ(environ: dict) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(environ=environ)


class Executable:
    """
    A thing that can be executed in a process.
    """

    def __init__(self,
                 is_shell: bool,
                 arg_list_or_str):
        self._is_shell = is_shell
        self._arg_list_or_str = arg_list_or_str

    @property
    def arg_list_or_str(self):
        """
        :return: Either a string or an iterable of strings
        """
        return self._arg_list_or_str

    @property
    def is_shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        return self._is_shell
