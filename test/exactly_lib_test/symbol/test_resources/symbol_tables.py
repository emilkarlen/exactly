from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_utils import container


def singleton_symbol_table_3(name: str, sdv: SymbolDependentValue) -> SymbolTable:
    return SymbolTable({name: container(sdv)})
