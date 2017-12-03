from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    HierarchyGeneratorEnvironment, \
    SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.targets import NullCustomTargetInfoFactory
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.utils import section_item_contents_as_section_contents


class SectionContentsConstructorFromHierarchyGenerator(SectionContentsConstructor):
    """
    Transforms a `SectionGenerator` to a `SectionContentsRenderer`,
    for usages where section header and target hierarchy is irrelevant.
    """

    def __init__(self, generator: SectionHierarchyGenerator):
        self.generator = generator

    def apply(self, environment: ConstructionEnvironment) -> SectionContents:
        target_factory = NullCustomTargetInfoFactory()
        section_item = self.generator.generator_node(target_factory).section_item(HierarchyGeneratorEnvironment(set()),
                                                                                  environment)
        return section_item_contents_as_section_contents(section_item)
