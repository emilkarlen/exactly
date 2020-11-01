from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.util.symbol_table import SymbolTable


class SymbolDependentValueForTest(SymbolDependentValue):
    def resolve(self, symbols: SymbolTable):
        raise ValueError('unsupported')
