import itertools
from typing import Iterable, Optional, Set

from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.paragraph import ParagraphItemsConstructor
from exactly_lib.util.textformat.constructor.section import SectionContentsConstructor, \
    ArticleContentsConstructor, SectionConstructor, ArticleConstructor
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfo
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib.util.textformat.structure.core import Text
from exactly_lib.util.textformat.structure.document import ArticleContents


def constant_contents(section_contents: docs.SectionContents) -> SectionContentsConstructor:
    return _ConstantSectionContentsConstructor(section_contents)


def contents(initial_paragraphs: ParagraphItemsConstructor = paragraphs.empty(),
             sub_sections: Iterable[SectionConstructor] = (),
             ) -> SectionContentsConstructor:
    return _SectionContents([initial_paragraphs],
                            sub_sections)


def contents_from_article_contents(article_contents: ArticleContentsConstructor) -> SectionContentsConstructor:
    return _SectionContentsFromArticleContentsConstructor(article_contents)


def section(header: Text,
            section_contents: SectionContentsConstructor) -> SectionConstructor:
    return _SectionConstructorFromSectionContentsConstructor(header,
                                                             section_contents)


def article(node_target_info: TargetInfo,
            contents_renderer: ArticleContentsConstructor,
            tags: Optional[Set[str]] = None,
            ) -> ArticleConstructor:
    return _ArticleConstructorFromContentsConstructor(node_target_info,
                                                      contents_renderer,
                                                      tags)


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


class _ArticleConstructorFromContentsConstructor(ArticleConstructor):
    def __init__(self,
                 node_target_info: TargetInfo,
                 contents_renderer: ArticleContentsConstructor,
                 tags: Optional[Set[str]] = None,
                 ):
        self._node_target_info = node_target_info
        self._tags = frozenset() if tags is None else tags
        self._contents_renderer = contents_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.Article:
        article_contents = self._contents_renderer.apply(environment)
        return doc.Article(self._node_target_info.presentation_text,
                           ArticleContents(article_contents.abstract_paragraphs,
                                           article_contents.section_contents),
                           target=self._node_target_info.target,
                           tags=self._tags)
