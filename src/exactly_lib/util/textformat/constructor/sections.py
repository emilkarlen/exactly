import itertools

from typing import List, Optional

from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import SectionContentsConstructor, \
    ArticleContentsConstructor, SectionConstructor
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text


class SectionContentsConstructorFromParagraphItemsConstructor(SectionContentsConstructor):
    def __init__(self, paragraph_item_constructors: List[ParagraphItemsConstructor]):
        self._paragraph_item_constructors = paragraph_item_constructors

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        initial_paragraphs = list(itertools.chain.from_iterable([
            renderer.apply(environment)
            for renderer in self._paragraph_item_constructors
        ]))
        return doc.SectionContents(initial_paragraphs)


class SectionContentsConstructorFromArticleContentsConstructor(SectionContentsConstructor):
    def __init__(self, article_contents_renderer: ArticleContentsConstructor):
        self._article_contents_renderer = article_contents_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        article_contents = self._article_contents_renderer.apply(environment)
        return article_contents.combined_as_section_contents


class SectionConstructorFromSectionContentsConstructor(SectionConstructor):
    def __init__(self,
                 header: Text,
                 section_contents_renderer: SectionContentsConstructor
                 ):
        self.header = header
        self.section_contents_renderer = section_contents_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.Section:
        return doc.Section(self.header,
                           self.section_contents_renderer.apply(environment))


def section_contents_constructor_with_sub_sections(
        section_constructor_list: List[SectionConstructor],
        initial_paragraphs: Optional[List[ParagraphItem]] = None) -> SectionContentsConstructor:
    return _SectionContentsConstructorWithSubSections(section_constructor_list,
                                                      initial_paragraphs if initial_paragraphs is not None else [])


class _SectionContentsConstructorWithSubSections(SectionContentsConstructor):
    def __init__(self,
                 section_constructor_list: List[SectionConstructor],
                 initial_paragraphs: List[ParagraphItem]):
        self.section_constructor_list = section_constructor_list
        self.initial_paragraphs = initial_paragraphs

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return doc.SectionContents(self.initial_paragraphs,
                                   [section_constructor.apply(environment)
                                    for section_constructor in self.section_constructor_list])


class SectionContentsConstructorForConstantContents(SectionContentsConstructor):
    def __init__(self, section_contents: doc.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return self.section_contents


def constant_section_contents(contents: docs.SectionContents) -> SectionContentsConstructor:
    return SectionContentsConstructorForConstantContents(contents)
