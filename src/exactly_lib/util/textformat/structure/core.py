from abc import ABC, abstractmethod
from typing import Set, Optional, TypeVar, Generic


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


T = TypeVar('T')


class TextVisitor(Generic[T], ABC):
    @abstractmethod
    def visit_string(self, text: 'StringText') -> T:
        pass

    @abstractmethod
    def visit_cross_reference(self, text: 'CrossReferenceText') -> T:
        pass

    @abstractmethod
    def visit_anchor(self, text: 'AnchorText') -> T:
        pass


class Text(TaggedItem, ABC):
    @abstractmethod
    def accept(self, visitor: TextVisitor[T]) -> T:
        pass


class ConcreteText(Text, ABC):
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

    def accept(self, visitor: TextVisitor[T]) -> T:
        return visitor.visit_string(self)


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

    def accept(self, visitor: TextVisitor[T]) -> T:
        return visitor.visit_cross_reference(self)


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

    def accept(self, visitor: TextVisitor[T]) -> T:
        return visitor.visit_anchor(self)


class ParagraphItem:
    """
    An item that is an element of a paragraph-level sequence of elements.
    """
    pass
