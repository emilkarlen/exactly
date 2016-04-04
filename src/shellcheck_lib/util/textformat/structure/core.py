class Text:
    pass


class ConcreteText(Text):
    pass


class StringText(ConcreteText):
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class CrossReferenceTarget:
    """
    A target used by anchors and cross references.

    The actual representation is meant to be application specific,
    so this class is purposely empty.
    """
    pass


class CrossReferenceText(ConcreteText):
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


class AnchorText(Text):
    """
    An anchor is an invisible target together with a visible text.
    """

    def __init__(self,
                 anchor: CrossReferenceTarget,
                 concrete_text: ConcreteText):
        self.anchor = anchor
        self.concrete_text = concrete_text


class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass
