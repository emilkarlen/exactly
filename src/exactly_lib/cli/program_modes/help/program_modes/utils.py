from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment, \
    SectionContentsConstructor, \
    ArticleContentsConstructor, SectionContentsConstructorFromArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import text, Text


def with_or_without_name(do_include_name: bool,
                         name: str,
                         contents_renderer: ArticleContentsConstructor) -> SectionContentsConstructor:
    if do_include_name:
        return _WithElementNameConstructor(text(name), contents_renderer)
    else:
        return SectionContentsConstructorFromArticleContentsConstructor(contents_renderer)


class _WithElementNameConstructor(SectionContentsConstructor):
    def __init__(self,
                 header: Text,
                 contents_constructor: ArticleContentsConstructor):
        self.header = header
        self.contents_constructor = contents_constructor

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        article_contents = self.contents_constructor.apply(environment)
        return doc.SectionContents([],
                                   [doc.Section(self.header,
                                                article_contents.combined_as_section_contents)])
