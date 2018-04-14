import pathlib
from typing import List

from exactly_lib.util.process_execution.command import Command, ProgramAndArguments, CommandDriver


class CommandDriverForShell(CommandDriver):
    def __init__(self, command_line: str):
        self._command_line = command_line

    @property
    def is_shell(self) -> bool:
        return True

    def arg_list_or_str_for(self, arguments: List[str]):
        return self.shell_command_line_with_args(arguments)

    @property
    def shell_command_line(self) -> str:
        return self._command_line

    def shell_command_line_with_args(self, arguments: List[str]) -> str:
        return ' '.join([self._command_line] + arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._command_line)


class CommandDriverForSystemProgram(CommandDriver):
    def __init__(self, program: str):
        self._program = program

    @property
    def is_shell(self) -> bool:
        return False

    def arg_list_or_str_for(self, arguments: List[str]):
        return [self._program] + arguments

    @property
    def program(self) -> str:
        return self._program

    def as_program_and_args(self, arguments: List[str]) -> ProgramAndArguments:
        return ProgramAndArguments(self._program, arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._program)


class CommandDriverForExecutableFile(CommandDriver):
    def __init__(self, executable_file: pathlib.Path):
        self._executable_file = executable_file

    @property
    def is_shell(self) -> bool:
        return False

    def arg_list_or_str_for(self, arguments: List[str]):
        return [str(self._executable_file)] + arguments

    @property
    def executable_file(self) -> pathlib.Path:
        return self._executable_file

    def as_program_and_args(self, arguments: List[str]) -> ProgramAndArguments:
        return ProgramAndArguments(str(self._executable_file), arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._executable_file)


def system_program_command(program: str,
                           arguments: List[str] = None) -> Command:
    return Command(CommandDriverForSystemProgram(program),
                   [] if arguments is None else arguments)


def executable_program_command2(program_and_args: ProgramAndArguments) -> Command:
    return Command(CommandDriverForSystemProgram(program_and_args.program),
                   program_and_args.arguments)


def executable_file_command(program_file: pathlib.Path,
                            arguments: List[str] = None) -> Command:
    return Command(CommandDriverForExecutableFile(program_file),
                   [] if arguments is None else arguments)


def shell_command(command: str) -> Command:
    return Command(CommandDriverForShell(command), [])


class CommandDriverVisitor:
    """
    Visitor of :class:`CommandDriver`
    """

    def visit(self, value: CommandDriver):
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, CommandDriverForExecutableFile):
            return self.visit_executable_file(value)
        if isinstance(value, CommandDriverForSystemProgram):
            return self.visit_system_program(value)
        if isinstance(value, CommandDriverForShell):
            return self.visit_shell(value)
        raise TypeError('Unknown {}: {}'.format(Command, str(value)))

    def visit_shell(self, command: CommandDriverForShell):
        raise NotImplementedError()

    def visit_executable_file(self, command: CommandDriverForExecutableFile):
        raise NotImplementedError()

    def visit_system_program(self, command: CommandDriverForSystemProgram):
        raise NotImplementedError()
