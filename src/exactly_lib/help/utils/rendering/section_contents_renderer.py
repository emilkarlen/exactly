import itertools

from exactly_lib.help.utils.rendering.cross_reference import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib.util.textformat.structure.core import Text, ParagraphItem


class RenderingEnvironment(tuple):
    def __new__(cls,
                cross_ref_text_constructor: CrossReferenceTextConstructor,
                render_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   render_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def render_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]


class ParagraphItemsRenderer:
    def apply(self, environment: RenderingEnvironment) -> list:
        raise NotImplementedError()


class SectionContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()


class ArticleContentsRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.ArticleContents:
        raise NotImplementedError()


class SectionRenderer:
    def apply(self, environment: RenderingEnvironment) -> doc.Section:
        raise NotImplementedError()


class ParagraphItemsRendererConstant(ParagraphItemsRenderer):
    def __init__(self, paragraph_items: list):
        self._paragraph_items = paragraph_items

    def apply(self, environment: RenderingEnvironment) -> list:
        return self._paragraph_items


class SectionContentsRendererFromParagraphItemsRenderer(SectionContentsRenderer):
    def __init__(self, paragraph_item_renderer: list):
        self._paragraph_item_renderer = paragraph_item_renderer

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = list(itertools.chain.from_iterable([
            renderer.apply(environment)
            for renderer in self._paragraph_item_renderer
        ]))
        return doc.SectionContents(initial_paragraphs)


class SectionContentsRendererFromArticleContentsRenderer(SectionContentsRenderer):
    def __init__(self, article_contents_renderer: ArticleContentsRenderer):
        self._article_contents_renderer = article_contents_renderer

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        article = self._article_contents_renderer.apply(environment)
        initial_paragraphs = article.abstract_paragraphs + article.section_contents.initial_paragraphs
        sub_sections = article.section_contents.sections
        return doc.SectionContents(initial_paragraphs, sub_sections)


class SectionRendererFromSectionContentsRenderer(SectionRenderer):
    def __init__(self,
                 header: Text,
                 section_contents_renderer: SectionContentsRenderer
                 ):
        self.header = header
        self.section_contents_renderer = section_contents_renderer

    def apply(self, environment: RenderingEnvironment) -> doc.Section:
        return doc.Section(self.header,
                           self.section_contents_renderer.apply(environment))


def section_contents_renderer_with_sub_sections(
        section_renderer_list: list,
        initial_paragraphs: list = None) -> SectionContentsRenderer:
    return _SectionContentsRendererWithSubSections(section_renderer_list,
                                                   initial_paragraphs if initial_paragraphs is not None else [])


class _SectionContentsRendererWithSubSections(SectionContentsRenderer):
    def __init__(self, section_renderer_list: list,
                 initial_paragraphs: list):
        """
        :type section_renderer_list: :class:`SectionRenderer`
        :type initial_paragraphs: list of :class:`ParagraphItem`
        """
        self.section_renderer_list = section_renderer_list
        self.initial_paragraphs = initial_paragraphs

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(self.initial_paragraphs,
                                   [section_renderer.apply(environment)
                                    for section_renderer in self.section_renderer_list])


class SectionContentsRendererForConstantContents(SectionContentsRenderer):
    def __init__(self, section_contents: doc.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return self.section_contents


class ConstantSectionContentsRenderer(SectionContentsRenderer):
    def __init__(self, section_contents: docs.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return self.section_contents
