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


class SystemProgramCommand(ProgramCommand):
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


def system_program_command(program: str,
                           arguments: List[str] = None) -> SystemProgramCommand:
    return SystemProgramCommand(ProgramAndArguments(program,
                                                    [] if arguments is None else arguments))


def executable_program_command2(program_and_args: ProgramAndArguments) -> SystemProgramCommand:
    return SystemProgramCommand(program_and_args)


def executable_file_command(program_file: pathlib.Path,
                            arguments: List[str] = None) -> ExecutableFileCommand:
    return ExecutableFileCommand(program_file, [] if arguments is None else arguments)


def shell_command(command: str) -> ShellCommand:
    return ShellCommand(command)


class CommandVisitor:
    """
    Visitor of `Command`
    """

    def visit(self, value: Command):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, ExecutableFileCommand):
            return self._visit_executable_file(value)
        if isinstance(value, SystemProgramCommand):
            return self._visit_system_program(value)
        if isinstance(value, ShellCommand):
            return self._visit_shell(value)
        raise TypeError('Unknown {}: {}'.format(Command, str(value)))

    def _visit_shell(self, command: ShellCommand):
        raise NotImplementedError()

    def _visit_executable_file(self, command: ExecutableFileCommand):
        raise NotImplementedError()

    def _visit_system_program(self, command: SystemProgramCommand):
        raise NotImplementedError()
