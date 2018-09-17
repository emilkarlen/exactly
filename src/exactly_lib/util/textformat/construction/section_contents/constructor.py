from typing import List

from exactly_lib.util.textformat.construction.section_hierarchy.targets import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.core import ParagraphItem


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
    def apply(self, environment: ConstructionEnvironment) -> List[ParagraphItem]:
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
