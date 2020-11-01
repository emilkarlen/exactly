from typing import Optional

from exactly_lib.symbol.sdv_structure import ReferenceRestrictions, SymbolContainer, Failure
from exactly_lib.util.symbol_table import SymbolTable


class UnconditionallyValidReferenceRestrictions(ReferenceRestrictions):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer,
                        ) -> Optional[Failure]:
        return None
