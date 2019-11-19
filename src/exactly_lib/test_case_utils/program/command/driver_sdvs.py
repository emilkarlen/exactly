from typing import Sequence

from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandDriverSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.type_system.logic.program import commands
from exactly_lib.type_system.logic.program.command import CommandDriverDdv
from exactly_lib.util.symbol_table import SymbolTable


class CommandDriverSdvForExecutableFile(CommandDriverSdv):
    def __init__(self,
                 executable_file: PathSdv):
        super().__init__([ExistingExecutableFileValidator(executable_file)])
        self._executable_file = executable_file

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._executable_file.references

    @property
    def executable_file(self) -> PathSdv:
        return self._executable_file

    def resolve(self, symbols: SymbolTable) -> CommandDriverDdv:
        return commands.CommandDriverDdvForExecutableFile(self._executable_file.resolve(symbols))


class CommandDriverSdvForSystemProgram(CommandDriverSdv):
    def __init__(self,
                 program: StringSdv,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        super().__init__(validators)
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    @property
    def program(self) -> StringSdv:
        return self._program

    def resolve(self, symbols: SymbolTable) -> CommandDriverDdv:
        return commands.CommandDriverDdvForSystemProgram(self._program.resolve(symbols))


class CommandDriverSdvForShell(CommandDriverSdv):
    def __init__(self,
                 command_line: StringSdv,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        super().__init__(validators)
        self._command_line = command_line

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._command_line.references

    def resolve(self, symbols: SymbolTable) -> CommandDriverDdv:
        return commands.CommandDriverDdvForShell(self._command_line.resolve(symbols))
