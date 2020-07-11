from typing import Sequence, List

from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.logic.program.command import CommandDriverDdv
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import CommandDriver
from exactly_lib.util.description_tree import details
from exactly_lib.util.render import strings
from exactly_lib.util.str_.str_constructor import ToStringObject


class CommandDriverDdvForShell(CommandDriverDdv):
    def __init__(self, command_line: StringDdv):
        self._command_line = command_line

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return commands.CommandDriverForShell.new_structure_builder_for(
            strings.AsToStringObject(self._command_line.describer()),
            _arguments_as_to_string_objects(arguments)
        )

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForShell(self._command_line.value_of_any_dependency(tcds))


class CommandDriverDdvForExecutableFile(CommandDriverDdv):
    def __init__(self, exe_file: PathDdv):
        self._exe_file = exe_file
        self._validators = (ExistingExecutableFileValidator(exe_file),)

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return commands.CommandDriverForExecutableFile.new_structure_builder_for(
            details.String(strings.AsToStringObject(self._exe_file.describer().value)),
            _arguments_as_to_string_objects(arguments),
        )

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForExecutableFile(self._exe_file.value_of_any_dependency__d(tcds))


class CommandDriverDdvForSystemProgram(CommandDriverDdv):
    def __init__(self, program: StringDdv):
        self._program = program

    def structure_for(self, arguments: ListDdv) -> StructureBuilder:
        return commands.CommandDriverForSystemProgram.new_structure_builder_for(
            strings.AsToStringObject(self._program.describer()),
            _arguments_as_to_string_objects(arguments),
        )

    def value_of_any_dependency(self, tcds: Tcds) -> CommandDriver:
        return commands.CommandDriverForSystemProgram(self._program.value_of_any_dependency(tcds))


def _arguments_as_to_string_objects(arguments: ListDdv) -> List[ToStringObject]:
    return [
        strings.AsToStringObject(argument.describer())
        for argument in arguments.string_elements
    ]
