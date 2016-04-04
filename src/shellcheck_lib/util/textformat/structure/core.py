class Text:
    pass


class StringText(Text):
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class CrossReferenceTarget:
    pass


class CrossReferenceText(Text):
    def __init__(self,
                 title: str,
                 target: CrossReferenceTarget):
        self._title = title
        self._target = target

    @property
    def title(self) -> str:
        return self._title

    @property
    def target(self) -> CrossReferenceTarget:
        return self._target


class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass
