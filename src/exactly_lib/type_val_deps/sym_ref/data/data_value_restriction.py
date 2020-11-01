from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.util.symbol_table import SymbolTable


class ValueRestriction:
    """
    A restriction on a resolved symbol value in the symbol table.

    Since sometimes, the restriction on the resolved value can be checked
    just by looking at the SDV - the checking method is given the SDV
    instead of the resolved value.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :rtype ErrorMessageWithFixTip
        :return: None if satisfied
        """
        raise NotImplementedError()
