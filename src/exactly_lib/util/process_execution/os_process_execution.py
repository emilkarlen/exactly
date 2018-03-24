from typing import List


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


class Command:
    @property
    def args(self):
        """
        :return: Either a string or an iterable of strings
        """
        raise NotImplementedError('abstract method')

    @property
    def shell(self) -> bool:
        """
        Tells whether args should be executed as a shell command.
        """
        raise NotImplementedError('abstract method')


class ShellCommand(Command):
    def __init__(self, command_line: str):
        self._command_line = command_line

    @property
    def args(self) -> str:
        return self._command_line

    @property
    def shell(self) -> bool:
        return True


class ExecutableProgramCommand(Command):
    def __init__(self, program_and_args: List[str]):
        self._program_and_args = program_and_args

    @property
    def args(self) -> List[str]:
        return self._program_and_args

    @property
    def shell(self) -> bool:
        return False


def executable_program_command(program_and_args: List[str]) -> Command:
    return ExecutableProgramCommand(program_and_args)


def shell_command(command: str) -> Command:
    return ShellCommand(command)
