from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.util.symbol_table import SymbolTable


class ValueRestrictionFailure(tuple):
    def __new__(cls,
                message: str,
                how_to_fix: str = ''):
        return tuple.__new__(cls, (message, how_to_fix))

    @property
    def message(self) -> str:
        return self[0]

    @property
    def how_to_fix(self) -> str:
        return self[1]

    def __str__(self) -> str:
        return '%s{message=%s, how_to_fix=%s}' % (type(self),
                                                  self.message,
                                                  self.how_to_fix)


class ValueRestriction:
    """
    A restriction on a resolved symbol value in the symbol table.

    Since sometimes, the restriction on the resolved value can be checked
    just by looking at the resolver - the checking method is given the resolver
    instead of the resolved value.
    """

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> ValueRestrictionFailure:
        """
        :param symbol_table: A symbol table that contains all symbols that the checked value refer to.
        :param symbol_name: The name of the symbol that the restriction applies to
        :param container: The container of the value that the restriction applies to
        :rtype ValueRestrictionFailure
        :return: None if satisfied
        """
        raise NotImplementedError()
