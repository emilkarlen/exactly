import pathlib
from abc import ABC
from typing import List, Generic, TypeVar

from exactly_lib.definitions.primitives import program
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.logic.program.process_execution.command import Command, ProgramAndArguments, CommandDriver
from exactly_lib.util.description_tree import details, tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.str_.str_constructor import ToStringObject


class CommandDriverForShell(CommandDriver):
    NAME = program.SHELL_COMMAND_TOKEN

    def __init__(self, command_line: str):
        self._command_line = command_line

    @staticmethod
    def new_structure_builder_for(command_line: ToStringObject,
                                  arguments: List[ToStringObject]) -> StructureBuilder:
        ret_val = StructureBuilder(CommandDriverForShell.NAME).append_details(details.String(command_line))
        if arguments:
            ret_val.append_child(_ArgumentListRenderer(arguments))

        return ret_val

    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        return self.new_structure_builder_for(self._command_line, arguments)

    @property
    def is_shell(self) -> bool:
        return True

    def arg_list_or_str_for(self, arguments: List[str]) -> str:
        return self.shell_command_line_with_args(arguments)

    @property
    def shell_command_line(self) -> str:
        return self._command_line

    def shell_command_line_with_args(self, arguments: List[str]) -> str:
        return ' '.join([self._command_line] + arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._command_line)


class CommandDriverWithArgumentList(CommandDriver, ABC):
    def arg_list_or_str_for(self, arguments: List[str]) -> List[str]:
        pass


class CommandDriverForSystemProgram(CommandDriverWithArgumentList):
    _NAME = program.SYSTEM_PROGRAM_TOKEN

    def __init__(self, program: str):
        self._program = program

    @staticmethod
    def new_structure_builder_for(program: ToStringObject,
                                  arguments: List[ToStringObject]) -> StructureBuilder:
        return _structure_builder_w_argument_list(
            CommandDriverForSystemProgram._NAME,
            details.String(program),
            arguments,
        )

    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        return self.new_structure_builder_for(self._program, arguments)

    @property
    def is_shell(self) -> bool:
        return False

    def arg_list_or_str_for(self, arguments: List[str]) -> List[str]:
        return [self._program] + arguments

    @property
    def program(self) -> str:
        return self._program

    def as_program_and_args(self, arguments: List[str]) -> ProgramAndArguments:
        return ProgramAndArguments(self._program, arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._program)


class CommandDriverForExecutableFile(CommandDriverWithArgumentList):
    NAME = 'executable file'

    def __init__(self, executable_file: DescribedPath):
        self._executable_file = executable_file

    @staticmethod
    def new_structure_builder_for(executable_file: DetailsRenderer,
                                  arguments: List[ToStringObject]) -> StructureBuilder:
        return _structure_builder_w_argument_list(
            CommandDriverForExecutableFile.NAME,
            executable_file,
            arguments,
        )

    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        return self.new_structure_builder_for(
            custom_details.path_primitive_details_renderer(self._executable_file.describer),
            arguments,
        )

    @property
    def is_shell(self) -> bool:
        return False

    def arg_list_or_str_for(self, arguments: List[str]) -> List[str]:
        return [str(self._executable_file.primitive)] + arguments

    @property
    def executable_file(self) -> pathlib.Path:
        return self._executable_file.primitive

    def as_program_and_args(self, arguments: List[str]) -> ProgramAndArguments:
        return ProgramAndArguments(str(self._executable_file.primitive), arguments)

    def __str__(self) -> str:
        return '{}({})'.format(type(self),
                               self._executable_file)


def system_program_command(program: str,
                           arguments: List[str] = None) -> Command:
    return Command(CommandDriverForSystemProgram(program),
                   [] if arguments is None else arguments)


def executable_file_command(program_file: DescribedPath,
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
        raise TypeError('Unknown {}: {}'.format(CommandDriver, str(value)))

    def visit_shell(self, command: CommandDriverForShell):
        raise NotImplementedError()

    def visit_executable_file(self, command: CommandDriverForExecutableFile):
        raise NotImplementedError()

    def visit_system_program(self, command: CommandDriverForSystemProgram):
        raise NotImplementedError()


T = TypeVar('T')


class CommandDriverArgumentTypePseudoVisitor(Generic[T], ABC):
    def visit(self, driver: CommandDriver) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(driver, CommandDriverWithArgumentList):
            return self.visit_with_argument_list(driver)
        if isinstance(driver, CommandDriverForShell):
            return self.visit_shell(driver)
        raise TypeError('Unknown {}: {}'.format(CommandDriver, str(driver)))

    def visit_shell(self, driver: CommandDriverForShell) -> T:
        raise NotImplementedError()

    def visit_with_argument_list(self, driver: CommandDriverWithArgumentList) -> T:
        raise NotImplementedError()


def _structure_builder_w_argument_list(name: str,
                                       program: DetailsRenderer,
                                       arguments: List[ToStringObject]) -> StructureBuilder:
    ret_val = StructureBuilder(name)
    ret_val.append_details(program)
    if len(arguments) != 0:
        ret_val.append_child(_ArgumentListRenderer(arguments))

    return ret_val


class _ArgumentListRenderer(NodeRenderer[None]):
    NAME = 'arguments'

    def __init__(self, arguments: List[ToStringObject]):
        self._arguments = arguments

    def render(self) -> tree.Node[None]:
        return tree.Node(
            self.NAME,
            None,
            [tree.StringDetail(argument)
             for argument in self._arguments],
            (),
        )
