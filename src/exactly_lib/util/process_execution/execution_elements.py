from types import MappingProxyType
from typing import Optional, Union, Sequence, Mapping


class ProcessExecutionSettings(tuple):
    def __new__(cls,
                timeout_in_seconds: Optional[int] = None,
                environ: Optional[Mapping[str, str]] = None,
                ):
        """
        :param environ: Must be immutable
        """
        return tuple.__new__(cls, (timeout_in_seconds, environ))

    @staticmethod
    def from_non_immutable(timeout_in_seconds: Optional[int] = None,
                           environ: Optional[Mapping[str, str]] = None) -> 'ProcessExecutionSettings':
        environ__ro = (
            None
            if environ is None
            else
            MappingProxyType(environ)
        )
        return ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds,
                                        environ=environ__ro)

    @staticmethod
    def with_timeout(timeout_in_seconds: Optional[int]) -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(timeout_in_seconds=timeout_in_seconds)

    @staticmethod
    def with_environ(environ: Mapping[str, str]) -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(environ=MappingProxyType(environ))

    @staticmethod
    def with_empty_environ() -> 'ProcessExecutionSettings':
        return ProcessExecutionSettings(environ=MappingProxyType({}))

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
    def environ(self) -> Optional[Mapping[str, str]]:
        """
        :return: (immutable) None if inherit current process' environment
        """
        return self[1]


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
