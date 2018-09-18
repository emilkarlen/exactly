from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc


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
