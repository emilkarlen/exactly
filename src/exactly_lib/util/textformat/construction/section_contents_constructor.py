import itertools

from exactly_lib.util.textformat.construction.section_hierarchy.targets import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc, structures as docs
from exactly_lib.util.textformat.structure.core import Text, ParagraphItem


class ConstructionEnvironment(tuple):
    def __new__(cls,
                cross_ref_text_constructor: CrossReferenceTextConstructor,
                construct_simple_header_value_lists_as_tables: bool = False):
        return tuple.__new__(cls, (cross_ref_text_constructor,
                                   construct_simple_header_value_lists_as_tables))

    @property
    def cross_ref_text_constructor(self) -> CrossReferenceTextConstructor:
        return self[0]

    @property
    def construct_simple_header_value_lists_as_tables(self) -> bool:
        return self[1]


class ParagraphItemsConstructor:
    def apply(self, environment: ConstructionEnvironment) -> list:
        raise NotImplementedError()


class SectionContentsConstructor:
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        raise NotImplementedError()


class ArticleContentsConstructor:
    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        raise NotImplementedError()


class SectionItemConstructor:
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionItem:
        raise NotImplementedError()


class SectionConstructor(SectionItemConstructor):
    def apply(self, environment: ConstructionEnvironment) -> doc.Section:
        raise NotImplementedError()


class ArticleConstructor(SectionItemConstructor):
    def apply(self, environment: ConstructionEnvironment) -> doc.Article:
        raise NotImplementedError()


class ParagraphItemsConstructorConstant(ParagraphItemsConstructor):
    def __init__(self, paragraph_items: list):
        self._paragraph_items = paragraph_items

    def apply(self, environment: ConstructionEnvironment) -> list:
        return self._paragraph_items


class SectionContentsConstructorFromParagraphItemsConstructor(SectionContentsConstructor):
    def __init__(self, paragraph_item_renderer: list):
        self._paragraph_item_renderer = paragraph_item_renderer

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        initial_paragraphs = list(itertools.chain.from_iterable([
            renderer.apply(environment)
            for renderer in self._paragraph_item_renderer
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
        section_constructor_list: list,
        initial_paragraphs: list = None) -> SectionContentsConstructor:
    return _SectionContentsConstructorWithSubSections(section_constructor_list,
                                                      initial_paragraphs if initial_paragraphs is not None else [])


class _SectionContentsConstructorWithSubSections(SectionContentsConstructor):
    def __init__(self,
                 section_constructor_list: list,
                 initial_paragraphs: list):
        """
        :type section_constructor_list: :class:`SectionConstructor`
        :type initial_paragraphs: list of :class:`ParagraphItem`
        """
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


class ConstantSectionContentsConstructor(SectionContentsConstructor):
    def __init__(self, section_contents: docs.SectionContents):
        self.section_contents = section_contents

    def apply(self, environment: ConstructionEnvironment) -> docs.SectionContents:
        return self.section_contents
