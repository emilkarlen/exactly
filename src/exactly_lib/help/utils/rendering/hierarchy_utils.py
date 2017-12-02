from exactly_lib.help_texts.cross_reference_id import TheCustomTargetInfoFactory
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy_constructor import HierarchyRenderingEnvironment, \
    SectionHierarchyGenerator
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
        target_factory = TheCustomTargetInfoFactory('ignored')
        section_item = self.generator.renderer_node(target_factory).section_item(HierarchyRenderingEnvironment(set()),
                                                                                 environment)
        return section_item_contents_as_section_contents(section_item)
