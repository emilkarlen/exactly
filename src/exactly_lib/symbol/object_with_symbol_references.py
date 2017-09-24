import itertools


class ObjectWithSymbolReferences:
    @property
    def references(self) -> list:
        """
        All :class:`NamedElementReference` directly referenced by this object.

        :rtype list of :class:`NamedElementReference`
        """
        return []


def references_from_objects_with_symbol_references(object_with_symbol_references_iterable) -> list:
    """Concatenates the references from a list of :class:`ObjectWithSymbolReferences`"""
    return list(itertools.chain.from_iterable([x.references
                                               for x in object_with_symbol_references_iterable]))
