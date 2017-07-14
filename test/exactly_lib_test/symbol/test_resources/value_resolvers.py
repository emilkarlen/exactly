from exactly_lib.symbol import string_resolver
from exactly_lib.symbol import symbol_usage
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


def string_resolver_of_single_symbol_reference(
        symbol_name: str,
        restrictions: ReferenceRestrictions = no_restrictions()) -> StringResolver:
    symbol_reference = symbol_usage.SymbolReference(symbol_name,
                                                    restrictions)
    fragments = [
        string_resolver.SymbolStringFragmentResolver(symbol_reference)
    ]
    return StringResolver(tuple(fragments))


class ConstantValueResolver(SymbolValueResolver):
    def __init__(self,
                 value_type: ValueType,
                 value: DirDependentValue):
        self._value_type = value_type
        self._value = value

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def references(self) -> list:
        return []

    def resolve(self, symbols: SymbolTable) -> DirDependentValue:
        return self._value
