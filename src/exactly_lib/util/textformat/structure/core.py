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
                 target: CrossReferenceTarget,
                 target_is_id_in_same_document: bool = True,
                 allow_rendering_of_visible_extra_target_text: bool = True):
        self._title = title
        self._target = target
        self._target_is_id_in_same_document = target_is_id_in_same_document
        self._allow_rendering_of_visible_extra_target_text = allow_rendering_of_visible_extra_target_text

    @property
    def title(self) -> str:
        return self._title

    @property
    def target(self) -> CrossReferenceTarget:
        return self._target

    @property
    def target_is_id_in_same_document(self) -> bool:
        return self._target_is_id_in_same_document

    @property
    def allow_rendering_of_visible_extra_target_text(self) -> bool:
        return self._allow_rendering_of_visible_extra_target_text


class AnchorText(Text):
    """
    An anchor is an invisible target together with a visible text.
    """

    def __init__(self,
                 anchor: CrossReferenceTarget,
                 anchored_text: ConcreteText):
        self._anchor = anchor
        self._anchored_text = anchored_text

    @property
    def anchor(self) -> CrossReferenceTarget:
        return self._anchor

    @property
    def anchored_text(self) -> ConcreteText:
        return self._anchored_text


class TextVisitor:
    def visit(self, text: Text):
        if isinstance(text, StringText):
            return self.visit_string(text)
        if isinstance(text, CrossReferenceText):
            return self.visit_cross_reference(text)
        if isinstance(text, AnchorText):
            return self.visit_anchor(text)
        raise ValueError('Not a value of sub type of %s: %s' % (str(Text), str(text)))

    def visit_string(self, text: StringText):
        raise NotImplementedError()

    def visit_cross_reference(self, text: CrossReferenceText):
        raise NotImplementedError()

    def visit_anchor(self, text: AnchorText):
        raise NotImplementedError()


class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass
