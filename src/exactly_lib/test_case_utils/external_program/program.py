from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.util.process_execution.os_process_execution import Command


class Program(tuple):
    def __new__(cls,
                command: Command,
                transformation: LinesTransformer):
        return tuple.__new__(cls, (command, transformation))

    @property
    def command(self) -> Command:
        return self[0]

    @property
    def transformation(self) -> LinesTransformer:
        return self[1]


class ProgramResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 command: CommandResolver,
                 transformations: Sequence[LinesTransformerResolver]
                 ):
        self._command = command
        self._transformations = transformations

    def new_with_additional_arguments(self,
                                      additional_arguments: ListResolver,
                                      additional_validation: Sequence[PreOrPostSdsValidator] = ()):
        """
        Creates a new resolver with additional arguments appended at the end of
        current argument list.
        """
        return ProgramResolver(
            self._command.new_with_additional_arguments(additional_arguments,
                                                        additional_validation),
            self._transformations)

    def new_with_additional_transformations(self,
                                            transformations: Sequence[LinesTransformerResolver]):
        """
        Creates a new resolver with additional transformation appended at the end of
        current transformations.
        """
        return ProgramResolver(
            self._command,
            tuple(self._transformations) + tuple(transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._command,
            self._transformations])
