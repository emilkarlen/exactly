import itertools
from typing import Sequence, List


class ObjectWithSymbolReferences:
    @property
    def references(self) -> Sequence:
        """
        All :class:`SymbolReference` directly referenced by this object.
        """
        return []


def references_from_objects_with_symbol_references(objects: Sequence[ObjectWithSymbolReferences]) -> List:
    """Concatenates the references from a list of :class:`ObjectWithSymbolReferences`"""
    return list(itertools.chain.from_iterable([x.references
                                               for x in objects]))
