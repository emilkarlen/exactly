from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_utils import container


def singleton_symbol_table_3(name: str, resolver: SymbolValueResolver) -> SymbolTable:
    return SymbolTable({name: container(resolver)})
