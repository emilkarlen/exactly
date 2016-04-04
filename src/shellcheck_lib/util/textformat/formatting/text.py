from shellcheck_lib.util.textformat.structure import core


class CrossReferenceFormatter:
    def apply(self, cross_reference: core.CrossReferenceText) -> str:
        raise NotImplementedError()


class TextFormatter:
    def __init__(self,
                 cross_reference_formatter: CrossReferenceFormatter):
        self._cross_reference_formatter = cross_reference_formatter

    def apply(self, text: core.Text) -> str:
        if isinstance(text, core.StringText):
            return text.value
        elif isinstance(text, core.CrossReferenceText):
            return self._cross_reference_formatter.apply(text)
        elif isinstance(text, core.AnchorText):
            return self.apply(text.concrete_text)
        else:
            raise ValueError('Text is neither a %s nor a %s: %s' % (str(core.Text),
                                                                    str(core.CrossReferenceText),
                                                                    str(text)))
