"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import CustomTargetInfoFactory
from exactly_lib.help.utils.entity_documentation import sorted_entity_list, EntityDocumentation
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.section_hierarchy_rendering import SectionGenerator, SectionRendererNode, \
    LeafSectionRendererNode, SectionRendererNodeWithSubSections
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class HtmlDocGeneratorForEntitiesHelp(SectionGenerator):
    def __init__(self,
                 header: str,
                 entity_2_section_contents_renderer: types.FunctionType,
                 all_entities: list,
                 rendering_environment: RenderingEnvironment,
                 ):
        """

        :param entity_2_section_contents_renderer: EntityDocumentation -> SectionContentsRenderer
        :param all_entities: [EntityDocumentation]
        """
        self.header = header
        self.entity_2_section_contents_renderer = entity_2_section_contents_renderer
        self.all_entities = all_entities
        self.rendering_environment = rendering_environment

    def section_renderer_node(self, target_factory: CustomTargetInfoFactory) -> SectionRendererNode:
        entity_nodes = [
            self._entity_node(entity)
            for entity in sorted_entity_list(self.all_entities)
        ]
        return SectionRendererNodeWithSubSections(target_factory.root(self.header),
                                                  [],
                                                  entity_nodes)

    def apply(self, targets_factory: CustomTargetInfoFactory) -> (list, doc.SectionContents):
        ret_val_sections = []
        ret_val_targets = []
        for entity in sorted_entity_list(self.all_entities):
            assert isinstance(entity, EntityDocumentation)
            entity_presentation_str = entity.singular_name()
            header = docs.anchor_text(docs.text(entity_presentation_str),
                                      entity.cross_reference_target())
            section_contents_renderer = self.entity_2_section_contents_renderer(entity)
            assert isinstance(section_contents_renderer, SectionContentsRenderer)
            section = doc.Section(header,
                                  section_contents_renderer.apply(self.rendering_environment))
            target_info_node = cross_ref.TargetInfoNode(cross_ref.TargetInfo(entity_presentation_str,
                                                                             entity.cross_reference_target()),
                                                        [])
            ret_val_sections.append(section)
            ret_val_targets.append(target_info_node)
        return ret_val_targets, doc.SectionContents([], ret_val_sections)

    def _entity_node(self, entity: EntityDocumentation) -> SectionRendererNode:
        target_info = cross_ref.TargetInfo(entity.singular_name(),
                                           entity.cross_reference_target())
        return LeafSectionRendererNode(target_info,
                                       self.entity_2_section_contents_renderer(entity))
