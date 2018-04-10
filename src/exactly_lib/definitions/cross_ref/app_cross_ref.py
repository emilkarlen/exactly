"""The base class for cross refs for the Exactly application."""
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget


class SeeAlsoTarget:
    """
    A target that can be presented as a see-also item
    """
    pass


class CrossReferenceId(CrossReferenceTarget, SeeAlsoTarget):
    """
    A part of the help text that can be referred to.

    The base class for all cross references used by Exactly.

    Supports equality.
    """

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self._eq_object_of_same_type(other)

    def _eq_object_of_same_type(self, other):
        raise NotImplementedError('abstract method')
