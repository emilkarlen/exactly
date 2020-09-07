from abc import ABC, abstractmethod
from typing import List, Optional, Set, TypeVar, Generic

from . import core

T = TypeVar('T')


class SectionItemVisitor(Generic[T], ABC):
    @abstractmethod
    def visit_section(self, section: 'Section') -> T:
        pass

    @abstractmethod
    def visit_article(self, article: 'Article') -> T:
        pass


class SectionItem(core.TaggedItem):
    def __init__(self,
                 header: core.Text,
                 target: Optional[core.CrossReferenceTarget],
                 tags: Optional[Set[str]]):
        self._header = header
        self._target = target
        self._tags = set() if tags is None else tags

    @property
    def header(self) -> core.Text:
        return self._header

    @property
    def target(self) -> Optional[core.CrossReferenceTarget]:
        """
        :return: Not None if this item serves as a cross ref target
        """
        return self._target

    @property
    def tags(self) -> Set[str]:
        return self._tags

    @abstractmethod
    def accept(self, visitor: SectionItemVisitor[T]) -> T:
        pass


class SectionContents(tuple):
    def __new__(cls,
                initial_paragraphs: List[core.ParagraphItem],
                sections: Optional[List[SectionItem]] = None):
        return tuple.__new__(cls, (initial_paragraphs,
                                   [] if sections is None else sections))

    @staticmethod
    def empty() -> 'SectionContents':
        return SectionContents([], None)

    @property
    def initial_paragraphs(self) -> List[core.ParagraphItem]:
        return self[0]

    @property
    def sections(self) -> List[SectionItem]:
        return self[1]

    @property
    def is_empty(self) -> bool:
        return not self.initial_paragraphs and not self.sections


class ArticleContents(tuple):
    def __new__(cls,
                abstract_paragraphs: List[core.ParagraphItem],
                section_contents: SectionContents):
        return tuple.__new__(cls, (abstract_paragraphs,
                                   section_contents))

    @property
    def abstract_paragraphs(self) -> List[core.ParagraphItem]:
        return self[0]

    @property
    def section_contents(self) -> SectionContents:
        return self[1]

    @property
    def combined_as_section_contents(self) -> SectionContents:
        initial_paragraphs = self.abstract_paragraphs + self.section_contents.initial_paragraphs
        return SectionContents(initial_paragraphs,
                               self.section_contents.sections)

    @property
    def is_empty(self) -> bool:
        return not self.abstract_paragraphs and self.section_contents.is_empty


class Section(SectionItem):
    def __init__(self,
                 header: core.Text,
                 contents: SectionContents,
                 target: Optional[core.CrossReferenceTarget] = None,
                 tags: Optional[Set[str]] = None):
        super().__init__(header, target, tags)
        self._contents = contents

    @property
    def contents(self) -> SectionContents:
        return self._contents

    def accept(self, visitor: SectionItemVisitor[T]) -> T:
        return visitor.visit_section(self)


class Article(SectionItem):
    """
    A section item with a semantic meaning of a self contained mini doc
    (corresponding to HTML article element).
    """

    def __init__(self,
                 header: core.Text,
                 contents: ArticleContents,
                 target: Optional[core.CrossReferenceTarget] = None,
                 tags: Optional[Set[str]] = None):
        super().__init__(header, target, tags)
        self._contents = contents

    @property
    def contents(self) -> ArticleContents:
        return self._contents

    def accept(self, visitor: SectionItemVisitor[T]) -> T:
        return visitor.visit_article(self)


def empty_section_contents() -> SectionContents:
    return SectionContents([], [])


def empty_article_contents() -> ArticleContents:
    return ArticleContents([], empty_section_contents())


def empty_section(header: core.Text) -> Section:
    return Section(header, empty_section_contents())


def empty_article(header: core.Text) -> Article:
    return Article(header, empty_article_contents())
