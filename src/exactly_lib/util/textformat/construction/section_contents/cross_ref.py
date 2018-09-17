from exactly_lib.util.textformat.structure.core import CrossReferenceTarget, Text


class CrossReferenceTextConstructor:
    def apply(self, x: CrossReferenceTarget) -> Text:
        raise NotImplementedError('abstract method')
