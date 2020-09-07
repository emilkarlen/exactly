from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNodeEnvironment
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory, TargetInfo
from exactly_lib.util.textformat.structure import document, core
from exactly_lib.util.textformat.structure.core import CrossReferenceTarget
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.utils import section_item_contents_as_section_contents


class SectionContentsConstructorFromHierarchyGenerator(SectionContentsConstructor):
    """
    Transforms a `SectionHierarchyGenerator` to a `SectionContentsConstructor`,
    for usages where section header and target hierarchy is irrelevant.
    """

    def __init__(self, generator: SectionHierarchyGenerator):
        self.generator = generator
        self._targets_stripper = _TargetsStripper()

    def apply(self, environment: ConstructionEnvironment) -> SectionContents:
        target_factory = _NullTargetInfoFactory()
        section_item = self.generator.generate(target_factory).section_item(SectionItemNodeEnvironment(set()),
                                                                            environment)
        section_item = section_item.accept(self._targets_stripper)
        return section_item_contents_as_section_contents(section_item)


class _TargetsStripper(document.SectionItemVisitor[document.SectionItem]):
    def visit_section(self, section: document.Section) -> document.SectionItem:
        return document.Section(section.header,
                                self._strip_section_contents(section.contents),
                                None,
                                section.tags)

    def visit_article(self, article: document.Article) -> document.SectionItem:
        return document.Article(article.header,
                                self._strip_article_contents(article.contents),
                                None,
                                article.tags)

    def _strip_article_contents(self, contents: document.ArticleContents) -> document.ArticleContents:
        return document.ArticleContents(contents.abstract_paragraphs,
                                        self._strip_section_contents(contents.section_contents))

    def _strip_section_contents(self, contents: document.SectionContents) -> document.SectionContents:
        return document.SectionContents(contents.initial_paragraphs,
                                        [section.accept(self) for section in contents.sections]
                                        )


class _NullTargetInfoFactory(TargetInfoFactory):
    """A CustomTargetInfoFactory that build empty CrossReferenceTarget:s"""

    def root(self, presentation: core.StringText) -> TargetInfo:
        return TargetInfo(presentation, CrossReferenceTarget())

    def sub_factory(self, local_name: str) -> TargetInfoFactory:
        return self
