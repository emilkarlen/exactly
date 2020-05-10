from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessageWithFixTip(tuple):
    def __new__(cls,
                message: TextRenderer,
                how_to_fix: Optional[TextRenderer] = None):
        return tuple.__new__(cls, (message, how_to_fix))

    @property
    def message(self) -> TextRenderer:
        return self[0]

    @property
    def how_to_fix(self) -> Optional[TextRenderer]:
        return self[1]

    def __str__(self) -> str:
        from exactly_lib.util.simple_textstruct.file_printer_output import to_string
        return '%s{message=%s, how_to_fix=%s}' % (
            type(self),
            to_string.major_blocks(self.message.render_sequence()),
            (''
             if self.how_to_fix is None
             else to_string.major_blocks(self.how_to_fix.render_sequence())
             )
        )


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
