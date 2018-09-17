from typing import Set, Optional


class TaggedItem:
    @property
    def tags(self) -> Set[str]:
        """
        Tags, used for CSS etc.
        :rtype: set of strings
        """
        raise NotImplementedError('abstract method')


class CrossReferenceTarget:
    """
    A target used by anchors and cross references.

    The actual representation is meant to be application specific,
    so this class is purposely empty.
    """
    pass


class UrlCrossReferenceTarget(CrossReferenceTarget):
    """
    A target that is an URL.
    """

    def __init__(self, url: str):
        self._url = url

    @property
    def url(self) -> str:
        return self._url


class Text(TaggedItem):
    pass


class ConcreteText(Text):
    def __init__(self, tags: Optional[Set[str]] = None):
        self._tags = set() if tags is None else tags

    @property
    def tags(self) -> Set[str]:
        return self._tags


class StringText(ConcreteText):
    def __init__(self,
                 value: str,
                 tags: Optional[Set[str]] = None):
        super().__init__(tags)
        self._value = value

    @property
    def value(self) -> str:
        return self._value


class CrossReferenceText(ConcreteText):
    def __init__(self,
                 title: StringText,
                 target: CrossReferenceTarget,
                 target_is_id_in_same_document: bool = True,
                 allow_rendering_of_visible_extra_target_text: bool = True,
                 tags: Optional[Set[str]] = None):
        super().__init__(tags)
        self._title = title
        self._target = target
        self._target_is_id_in_same_document = target_is_id_in_same_document
        self._allow_rendering_of_visible_extra_target_text = allow_rendering_of_visible_extra_target_text

    @property
    def title_text(self) -> StringText:
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
                 anchored_text: ConcreteText,
                 anchor: CrossReferenceTarget):
        self._anchored_text = anchored_text
        self._anchor = anchor

    @property
    def anchor(self) -> CrossReferenceTarget:
        return self._anchor

    @property
    def anchored_text(self) -> ConcreteText:
        return self._anchored_text

    @property
    def tags(self) -> Set[str]:
        return self._anchored_text.tags


class TextVisitor:
    def visit(self, text: Text):
        if isinstance(text, StringText):
            return self.visit_string(text)
        if isinstance(text, CrossReferenceText):
            return self.visit_cross_reference(text)
        if isinstance(text, AnchorText):
            return self.visit_anchor(text)
        raise TypeError('Not a value of sub type of %s: %s' % (str(Text), str(text)))

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
