from exactly_lib.util.textformat.structure import core


class TargetRenderer:
    """
    Abstract base class for rendering of a cross reference target.
    """

    def apply(self, target: core.CrossReferenceTarget) -> str:
        raise NotImplementedError()
