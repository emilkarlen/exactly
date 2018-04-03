from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.lines_transformer import LinesTransformerSequenceResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.component_resolvers import StdinDataResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable


class ProgramResolverForCommand(ProgramResolver):
    def __init__(self,
                 command: CommandResolver,
                 stdin: StdinDataResolver,
                 transformations: Sequence[LinesTransformerResolver] = ()
                 ):
        self._stdin = stdin
        self._command = command
        self._transformations = transformations

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.PROGRAM

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    def new_accumulated(self,
                        additional_arguments: ListResolver,
                        additional_transformations: Sequence[LinesTransformerResolver],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ):
        return ProgramResolverForCommand(self._command.new_with_additional_arguments(additional_arguments,
                                                                                     additional_validation),
                                         self._stdin,
                                         tuple(self._transformations) + tuple(additional_transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = [self._command, self._stdin] + list(self._transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return tuple(self._command.validators) + tuple(self._stdin.validators)

    def resolve_value(self, symbols: SymbolTable) -> ProgramValue:
        return ProgramValue(self._command.resolve_value(symbols),
                            self._stdin.resolve_value(symbols),
                            LinesTransformerSequenceResolver(self._transformations).resolve(symbols))
