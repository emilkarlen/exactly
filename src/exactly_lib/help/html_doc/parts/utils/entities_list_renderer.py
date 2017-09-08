"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.help.contents_structure import EntityConfiguration, HtmlDocHierarchyGeneratorGetter
from exactly_lib.help.utils.entity_documentation import EntityDocumentation
from exactly_lib.help.utils.rendering.entity_documentation_rendering import sorted_entity_list
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionRendererNode, \
    LeafSectionRendererNode, SectionRendererNodeWithSubSections
from exactly_lib.help_texts import cross_reference_id as cross_ref


def hierarchy_generator(header: str,
                        entity_conf: EntityConfiguration,
                        ) -> SectionHierarchyGenerator:
    """
    Utility to make a hierarchy from an `EntityConfiguration`
    """
    return HtmlDocHierarchyGeneratorForEntitiesHelp(header,
                                                    entity_conf.entity_doc_2_section_contents_renderer,
                                                    entity_conf.entities_help.all_entities)


class FlatEntityListHierarchyGeneratorGetter(HtmlDocHierarchyGeneratorGetter):
    def __init__(self, entity_doc_2_section_contents_renderer):
        self._entity_doc_2_section_contents_renderer = entity_doc_2_section_contents_renderer

    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: list) -> SectionHierarchyGenerator:
        return HtmlDocHierarchyGeneratorForEntitiesHelp(header,
                                                        self._entity_doc_2_section_contents_renderer,
                                                        all_entity_doc_list)


class HtmlDocHierarchyGeneratorForEntitiesHelp(SectionHierarchyGenerator):
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

    def section_renderer_node(self, target_factory: cross_ref.CustomTargetInfoFactory) -> SectionRendererNode:
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
