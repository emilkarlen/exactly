from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference


class ObjectWithTypedSymbolReferences(ObjectWithSymbolReferences):
    """
    A variant of :class:`ObjectWithSymbolReferences` with
    more specific type hints.

    Would like to have these type hints in :class:`ObjectWithSymbolReferences`,
    but that is not possible for the moment due to circular dependencies.
    """

    @property
    def references(self) -> Sequence[SymbolReference]:
        """
        All :class:`SymbolReference` directly referenced by this object.
        """
        return []
