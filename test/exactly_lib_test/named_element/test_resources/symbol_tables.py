from exactly_lib.named_element.resolver_structure import NamedElementResolver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.test_resources.named_elem_utils import container


def singleton_symbol_table_3(name: str, resolver: NamedElementResolver) -> SymbolTable:
    return SymbolTable({name: container(resolver)})
