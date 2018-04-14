import pathlib
from typing import List

from exactly_lib.util.process_execution.command import Command, ProgramAndArguments


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
