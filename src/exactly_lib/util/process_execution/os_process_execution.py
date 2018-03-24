import pathlib
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


class ProgramAndArguments:
    def __init__(self,
                 program: str,
                 arguments: List[str]):
        self.program = program
        self.arguments = arguments


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

    @property
    def shell_command_line(self) -> str:
        raise ValueError('this object is not a shell command: ' + str(self.args))

    @property
    def program_and_arguments(self) -> ProgramAndArguments:
        raise ValueError('this object is not a program with arguments: ' + str(self.args))


class ShellCommand(Command):
    def __init__(self, command_line: str):
        self._command_line = command_line

    @property
    def args(self) -> str:
        return self._command_line

    @property
    def shell(self) -> bool:
        return True

    @property
    def shell_command_line(self) -> str:
        return self._command_line


class ProgramCommand(Command):
    @property
    def shell(self) -> bool:
        return False


class ExecutableProgramCommand(ProgramCommand):
    def __init__(self,
                 program_and_arguments: ProgramAndArguments):
        self._program_and_arguments = program_and_arguments

    @property
    def args(self) -> List[str]:
        return [self._program_and_arguments.program] + self._program_and_arguments.arguments

    @property
    def program_and_arguments(self) -> ProgramAndArguments:
        return self._program_and_arguments


class ExecutableFileCommand(ProgramCommand):
    def __init__(self,
                 executable_file: pathlib.Path,
                 arguments: List[str]):
        self._executable_file = executable_file
        self._arguments = arguments

    @property
    def args(self) -> List[str]:
        return [str(self._executable_file)] + self._arguments

    @property
    def program_and_arguments(self) -> ProgramAndArguments:
        return ProgramAndArguments(str(self._executable_file),
                                   self._arguments)


def executable_program_command(program: str,
                               arguments: List[str] = None) -> ProgramCommand:
    return ExecutableProgramCommand(ProgramAndArguments(program,
                                                        [] if arguments is None else arguments))


def executable_program_command2(program_and_args: ProgramAndArguments) -> ProgramCommand:
    return ExecutableProgramCommand(program_and_args)


def executable_file_command(program_file: pathlib.Path,
                            arguments: List[str] = None) -> ProgramCommand:
    return ExecutableFileCommand(program_file, [] if arguments is None else arguments)


def shell_command(command: str) -> ShellCommand:
    return ShellCommand(command)
