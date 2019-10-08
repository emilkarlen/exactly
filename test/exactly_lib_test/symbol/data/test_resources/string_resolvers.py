from typing import Sequence

from exactly_lib.symbol.data.string_resolver import StringResolver, StringFragmentResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.data.concrete_string_values import ConstantFragment
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.symbol_table import SymbolTable


def arbitrary_resolver() -> StringResolver:
    return StringResolverTestImpl('arbitrary value')


class StringResolverTestImpl(StringResolver):
    def __init__(self,
                 value: str,
                 explicit_references: Sequence[SymbolReference] = (),
                 fragment_resolvers: Sequence[StringFragmentResolver] = ()):
        super().__init__(fragment_resolvers)
        self.value = value
        self.explicit_references = explicit_references
        self._fragments = fragment_resolvers

    def resolve(self, symbols: SymbolTable) -> StringValue:
        return StringValue((ConstantFragment(self.value),))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.explicit_references
