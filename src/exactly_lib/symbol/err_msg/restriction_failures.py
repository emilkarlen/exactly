from typing import Sequence

from exactly_lib.symbol.sdv_structure import Failure
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessage(SequenceRenderer[MajorBlock]):
    def __init__(self,
                 failing_symbol: str,
                 symbols: SymbolTable,
                 failure: Failure,
                 ):
        self._failing_symbol = failing_symbol
        self._symbols = symbols
        self._failure = failure

    def render_sequence(self) -> Sequence[MajorBlock]:
        return self._failure.render(self._failing_symbol, self._symbols)
