from typing import Sequence

from exactly_lib.symbol.program import stdin_data_resolver
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.stdin_data_resolver import StdinDataResolver
from exactly_lib.symbol.resolver_structure import StringTransformerResolver, LogicValueResolver
from exactly_lib.symbol.resolver_with_validation import DirDepValueResolverWithValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable


class ProgramResolver(LogicValueResolver, DirDepValueResolverWithValidation[ProgramValue]):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.PROGRAM

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> ProgramValue:
        raise NotImplementedError('abstract method')

    def new_accumulated(self,
                        additional_stdin: StdinDataResolver,
                        additional_arguments: ArgumentsResolver,
                        additional_transformations: Sequence[StringTransformerResolver],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ):
        raise NotImplementedError('abstract method')

    def new_with_additional_arguments(self, additional_arguments: ArgumentsResolver):
        """
        Creates a new resolver with additional arguments appended at the end of
        current argument list.
        """
        return self.new_accumulated(stdin_data_resolver.no_stdin(),
                                    additional_arguments,
                                    (),
                                    ())

    def new_with_appended_transformations(self, transformations: Sequence[StringTransformerResolver]):
        """
        Creates a new resolver with additional transformation appended at the end of
        current transformations.
        """
        return self.new_accumulated(stdin_data_resolver.no_stdin(),
                                    arguments_resolvers.empty(),
                                    transformations,
                                    ())
