import itertools

from typing import Iterable

from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import SectionContentsConstructor, \
    ArticleContentsConstructor, SectionConstructor
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib.util.textformat.structure.core import Text


def paragraphs_contents(paragraphs: Iterable[ParagraphItemsConstructor]) -> SectionContentsConstructor:
    return contents(paragraphs)


def constant_contents(section_contents: docs.SectionContents) -> SectionContentsConstructor:
    return _ConstantSectionContentsConstructor(section_contents)


def contents(initial_paragraphs: Iterable[ParagraphItemsConstructor] = (),
             sub_sections: Iterable[SectionConstructor] = (),
             ) -> SectionContentsConstructor:
    return _SectionContents(initial_paragraphs,
                            sub_sections)


def contents_from_article_contents(article_contents: ArticleContentsConstructor) -> SectionContentsConstructor:
    return _SectionContentsFromArticleContentsConstructor(article_contents)


def section(header: Text,
            section_contents: SectionContentsConstructor) -> SectionConstructor:
    return _SectionConstructorFromSectionContentsConstructor(header,
                                                             section_contents)


class _SectionConstructorFromSectionContentsConstructor(SectionConstructor):
    def __init__(self,
                 header: Text,
                 section_contents_renderer: SectionContentsConstructor
                 ):
        self.header = header
        self.section_contents_renderer = section_contents_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.Section:
        return doc.Section(self.header,
                           self.section_contents_renderer.apply(environment))


class _SectionContentsFromArticleContentsConstructor(SectionContentsConstructor):
    def __init__(self, article_contents_renderer: ArticleContentsConstructor):
        self._article_contents_renderer = article_contents_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        article_contents = self._article_contents_renderer.apply(environment)
        return article_contents.combined_as_section_contents


class _SectionContents(SectionContentsConstructor):
    def __init__(self,
                 paragraph_items: Iterable[ParagraphItemsConstructor],
                 sub_sections: Iterable[SectionConstructor]):
        self._paragraph_items = paragraph_items
        self._sub_sections = sub_sections

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        initial_paragraphs = list(itertools.chain.from_iterable([
            renderer.apply(environment)
            for renderer in self._paragraph_items
        ]))
        sub_sections = [ss.apply(environment)
                        for ss in self._sub_sections]
        return doc.SectionContents(initial_paragraphs,
                                   sub_sections)


class _ConstantSectionContentsConstructor(SectionContentsConstructor):
    def __init__(self, section_contents_: doc.SectionContents):
        self.section_contents = section_contents_

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return self.section_contents
