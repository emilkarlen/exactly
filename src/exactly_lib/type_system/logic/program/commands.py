from typing import Sequence

from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.logic.program.command import CommandDriverDdv
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import CommandDriver
from exactly_lib.util.description_tree import tree, details
from exactly_lib.util.description_tree.renderer import DetailsRenderer, NodeRenderer
from exactly_lib.util.render import strings


class CommandDriverDdvForShell(CommandDriverDdv):
    def __init__(self, command_line: StringDdv):
        self._command_line = command_line

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return StructureBuilder(
            syntax_elements.SHELL_COMMAND_TOKEN,
        ).append_details(details.String(strings.AsToStringObject(self._command_line.describer())))

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(tcds))


class CommandDriverDdvForExecutableFile(CommandDriverDdv):
    def __init__(self, exe_file: PathDdv):
        self._exe_file = exe_file
        self._validators = (ExistingExecutableFileValidator(exe_file),)

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return _builder_w_argument_list(
            'executable file',
            details.String(strings.AsToStringObject(self._exe_file.describer().value)),
            arguments,
        )

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency(tcds))


class CommandDriverDdvForSystemProgram(CommandDriverDdv):
    def __init__(self, program: StringDdv):
        self._program = program

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return _builder_w_argument_list(
            syntax_elements.SYSTEM_PROGRAM_TOKEN,
            details.String(strings.AsToStringObject(self._program.describer())),
            arguments,
        )

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(tcds))


def _builder_w_argument_list(name: str, program: DetailsRenderer, arguments: ListDdv) -> StructureBuilder:
    ret_val = StructureBuilder(name)
    ret_val.append_details(program)
    if len(arguments.string_elements) != 0:
        ret_val.append_child(_ArgumentListRenderer(arguments))

    return ret_val


class _ArgumentListRenderer(NodeRenderer[None]):
    def __init__(self, arguments: ListDdv):
        self._arguments = arguments

    def render(self) -> tree.Node[None]:
        return tree.Node(
            'arguments',
            None,
            [tree.StringDetail(strings.AsToStringObject(argument.describer()))
             for argument in self._arguments.string_elements],
            (),
        )
