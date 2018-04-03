from typing import Sequence

from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.command_resolver import CommandDriverResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.validators import ExistingExecutableFileValidator
from exactly_lib.type_system.logic.program import command_values
from exactly_lib.type_system.logic.program.command_value import CommandValue
from exactly_lib.util.symbol_table import SymbolTable


class CommandDriverResolverForExecutableFile(CommandDriverResolver):
    def __init__(self,
                 executable_file: FileRefResolver):
        super().__init__([ExistingExecutableFileValidator(executable_file)])
        self._executable_file = executable_file

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._executable_file.references

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file

    def make(self,
             symbols: SymbolTable,
             arguments: ListResolver) -> CommandValue:
        return command_values.CommandValueForExecutableFile(self._executable_file.resolve(symbols),
                                                            arguments.resolve(symbols))


class CommandDriverResolverForSystemProgram(CommandDriverResolver):
    def __init__(self,
                 program: StringResolver,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        super().__init__(validators)
        self._program = program

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._program.references

    @property
    def program(self) -> StringResolver:
        return self._program

    def make(self,
             symbols: SymbolTable,
             arguments: ListResolver) -> CommandValue:
        return command_values.CommandValueForSystemProgram(self._program.resolve(symbols),
                                                           arguments.resolve(symbols))


class CommandDriverResolverForShell(CommandDriverResolver):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def make(self,
             symbols: SymbolTable,
             arguments: ListResolver) -> CommandValue:
        arguments_as_string = string_resolvers.from_list_resolver(arguments)
        # Quoting list elements using shlex here?
        return command_values.CommandValueForShell(arguments_as_string.resolve(symbols))
