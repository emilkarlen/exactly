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


class Command:
    @property
    def as_executable_tmp_method(self) -> Executable:
        return Executable(self.shell, self.args)

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

    @property
    def arguments(self) -> List[str]:
        raise NotImplementedError('abstract method')


class ExecutableProgramCommand(ProgramCommand):
    def __init__(self,
                 program_and_arguments: ProgramAndArguments):
        self._program_and_arguments = program_and_arguments

    @property
    def args(self) -> List[str]:
        return [self._program_and_arguments.program] + self._program_and_arguments.arguments

    @property
    def arguments(self) -> List[str]:
        return self._program_and_arguments.arguments

    @property
    def program(self) -> str:
        return self._program_and_arguments.program

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

    @property
    def executable_file(self) -> pathlib.Path:
        return self._executable_file

    @property
    def arguments(self) -> List[str]:
        return self._arguments


def executable_program_command(program: str,
                               arguments: List[str] = None) -> ExecutableProgramCommand:
    return ExecutableProgramCommand(ProgramAndArguments(program,
                                                        [] if arguments is None else arguments))


def executable_program_command2(program_and_args: ProgramAndArguments) -> ExecutableProgramCommand:
    return ExecutableProgramCommand(program_and_args)


def executable_file_command(program_file: pathlib.Path,
                            arguments: List[str] = None) -> ExecutableFileCommand:
    return ExecutableFileCommand(program_file, [] if arguments is None else arguments)


def shell_command(command: str) -> ShellCommand:
    return ShellCommand(command)
