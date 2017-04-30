"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.utils.entity_documentation import sorted_entity_list, EntityDocumentation
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionGenerator, SectionRendererNode, \
    LeafSectionRendererNode, SectionRendererNodeWithSubSections


class HtmlDocGeneratorForEntitiesHelp(SectionGenerator):
    def __init__(self,
                 header: str,
                 entity_2_section_contents_renderer: types.FunctionType,
                 all_entities: list):
        """

        :param entity_2_section_contents_renderer: EntityDocumentation -> SectionContentsRenderer
        :param all_entities: [EntityDocumentation]
        """
        self.header = header
        self.entity_2_section_contents_renderer = entity_2_section_contents_renderer
        self.all_entities = all_entities

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        entity_nodes = [
            self._entity_node(entity)
            for entity in sorted_entity_list(self.all_entities)
        ]
        return SectionRendererNodeWithSubSections(target_factory.root(self.header),
                                                  [],
                                                  entity_nodes)

    def _entity_node(self, entity: EntityDocumentation) -> SectionRendererNode:
        target_info = cross_ref.TargetInfo(entity.singular_name(),
                                           entity.cross_reference_target())
        return LeafSectionRendererNode(target_info,
                                       self.entity_2_section_contents_renderer(entity))
