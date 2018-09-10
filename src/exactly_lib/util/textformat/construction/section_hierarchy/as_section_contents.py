from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    HierarchyGeneratorEnvironment, \
    SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.targets import NullCustomTargetInfoFactory
from exactly_lib.util.textformat.structure import document
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
        target_factory = NullCustomTargetInfoFactory()
        section_item = self.generator.generator_node(target_factory).section_item(HierarchyGeneratorEnvironment(set()),
                                                                                  environment)
        section_item = self._targets_stripper.visit(section_item)
        return section_item_contents_as_section_contents(section_item)


class _TargetsStripper(document.SectionItemVisitor):
    def visit_section(self, section: document.Section):
        return document.Section(section.header,
                                self._strip_section_contents(section.contents),
                                None,
                                section.tags)

    def visit_article(self, article: document.Article):
        return document.Article(article.header,
                                self._strip_article_contents(article.contents),
                                None,
                                article.tags)

    def _strip_article_contents(self, contents: document.ArticleContents) -> document.ArticleContents:
        return document.ArticleContents(contents.abstract_paragraphs,
                                        self._strip_section_contents(contents.section_contents))

    def _strip_section_contents(self, contents: document.SectionContents) -> document.SectionContents:
        return document.SectionContents(contents.initial_paragraphs,
                                        list(map(self.visit, contents.sections)))
