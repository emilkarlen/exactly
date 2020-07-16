from typing import Dict, Optional, Union, Sequence


class ProcessExecutionSettings(tuple):
    def __new__(cls,
                timeout_in_seconds: Optional[int] = None,
                environ: Optional[Dict[str, str]] = None):
        return tuple.__new__(cls, (timeout_in_seconds, environ))

    @staticmethod
    def with_environ(environ: Dict[str, str]) -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(environ=environ)

    @staticmethod
    def with_empty_environ() -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(environ={})

    @staticmethod
    def with_environ_copy(environ_to_copy: Dict[str, str]) -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(environ=dict(environ_to_copy))

    @staticmethod
    def null() -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings()

    @property
    def timeout_in_seconds(self) -> Optional[int]:
        """
        :return: None if no timeout
        """
        return self[0]

    @property
    def environ(self) -> Optional[Dict[str, str]]:
        """
        :return: None if inherit current process' environment
        """
        return self[1]


def with_no_timeout() -> ProcessExecutionSettings:
    return ProcessExecutionSettings()


def with_environ(environ: Dict[str, str]) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(environ=environ)


def with_environ_copy(environ_to_copy: Dict[str, str]) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(environ=dict(environ_to_copy))


class Executable:
    """
    A thing that can be executed in a process.
    """

    def __init__(self,
                 is_shell: bool,
                 arg_list_or_str: Union[str, Sequence[str]]):
        self._is_shell = is_shell
        self._arg_list_or_str = arg_list_or_str

    @property
    def arg_list_or_str(self) -> Union[str, Sequence[str]]:
        return self._arg_list_or_str

    @property
    def is_shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        return self._is_shell
