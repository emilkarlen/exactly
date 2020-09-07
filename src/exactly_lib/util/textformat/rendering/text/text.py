from exactly_lib.util.textformat.structure import core


class CrossReferenceFormatter:
    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        raise NotImplementedError()


class TextFormatter(core.TextVisitor[str]):
    def __init__(self,
                 cross_reference_formatter: CrossReferenceFormatter):
        self._cross_reference_formatter = cross_reference_formatter

    def apply(self, text: core.Text) -> str:
        return text.accept(self)

    def visit_cross_reference(self, text: core.CrossReferenceText):
        return self._cross_reference_formatter.apply(text)

    def visit_anchor(self, text: core.AnchorText) -> str:
        return self.apply(text.anchored_text)

    def visit_string(self, text: core.StringText) -> str:
        return text.value
