from exactly_lib.util.textformat.structure.core import Text, CrossReferenceTarget


class CrossReferenceTextConstructor:
    def apply(self, x: CrossReferenceTarget) -> Text:
        raise NotImplementedError('abstract method')
