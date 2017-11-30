from . import core


class SectionContents(tuple):
    def __new__(cls,
                initial_paragraphs: list,
                sections: list = None):
        """
        :type initial_paragraphs: [core.ParagraphItem]
        :type sections: [SectionItem]
        """
        return tuple.__new__(cls, (initial_paragraphs,
                                   [] if sections is None else sections))

    @property
    def initial_paragraphs(self) -> list:
        """
        :return: [core.ParagraphItem]
        """
        return self[0]

    @property
    def sections(self) -> list:
        """
        :return: [SectionItem]
        """
        return self[1]

    @property
    def is_empty(self) -> bool:
        return not self.initial_paragraphs and not self.sections


class ArticleContents(tuple):
    def __new__(cls,
                abstract_paragraphs: list,
                section_contents: SectionContents):
        """
        :type abstract_paragraphs: [core.ParagraphItem]
        """
        return tuple.__new__(cls, (abstract_paragraphs,
                                   section_contents))

    @property
    def abstract_paragraphs(self) -> list:
        """
        :return: [core.ParagraphItem]
        """
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


class SectionItem(core.TaggedItem):
    def __init__(self,
                 header: core.Text,
                 target: core.CrossReferenceTarget,
                 tags: set):
        self._header = header
        self._target = target
        self._tags = set() if tags is None else tags

    @property
    def header(self) -> core.Text:
        return self._header

    @property
    def target(self) -> core.CrossReferenceTarget:
        """
        :return: Not None if this item serves as a cross ref target
        """
        return self._target

    @property
    def tags(self) -> set:
        return self._tags


class Section(SectionItem):
    def __init__(self,
                 header: core.Text,
                 contents: SectionContents,
                 target: core.CrossReferenceTarget = None,
                 tags: set = None):
        super().__init__(header, target, tags)
        self._contents = contents

    @property
    def contents(self) -> SectionContents:
        return self._contents


class Article(SectionItem):
    """
    A section item with a semantic meaning of a self contained mini doc
    (corresponding to HTML article element).
    """

    def __init__(self,
                 header: core.Text,
                 contents: ArticleContents,
                 target: core.CrossReferenceTarget = None,
                 tags: set = None):
        super().__init__(header, target, tags)
        self._contents = contents

    @property
    def contents(self) -> ArticleContents:
        return self._contents


def empty_section_contents() -> SectionContents:
    return SectionContents([], [])


def empty_article_contents() -> ArticleContents:
    return ArticleContents([], empty_section_contents())


def empty_section(header: core.Text) -> Section:
    return Section(header, empty_section_contents())


def empty_article(header: core.Text) -> Article:
    return Article(header, empty_article_contents())


class SectionItemVisitor:
    def visit(self, item: SectionItem):
        if isinstance(item, Section):
            return self.visit_section(item)
        elif isinstance(item, Article):
            return self.visit_article(item)
        else:
            raise TypeError('Unknown {}: {}'.format(SectionItem,
                                                    str(item)))

    def visit_section(self, section: Section):
        raise NotImplemented('abstract method')

    def visit_article(self, article: Article):
        raise NotImplemented('abstract method')
