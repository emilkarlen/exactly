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


def empty_contents() -> SectionContents:
    return SectionContents([], [])


class SectionItem:
    def __init__(self,
                 header: core.Text,
                 contents: SectionContents
                 ):
        self._header = header
        self._contents = contents

    @property
    def header(self) -> core.Text:
        return self._header

    @property
    def contents(self) -> SectionContents:
        return self._contents


class Section(SectionItem):
    pass


class Article(SectionItem):
    """
    A section item with a semantic meaning of a self contained mini doc
    (corresponding to HTML article element).
    """

    def __init__(self,
                 header: core.Text,
                 abstract_paragraphs: list,
                 contents: SectionContents
                 ):
        super().__init__(header, contents)
        self._abstract_paragraphs = abstract_paragraphs

    @property
    def abstract_paragraphs(self) -> list:
        return self._abstract_paragraphs


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
