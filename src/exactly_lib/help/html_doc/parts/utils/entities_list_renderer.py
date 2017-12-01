"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.help import std_tags
from exactly_lib.help.contents_structure import HtmlDocHierarchyGeneratorGetter
from exactly_lib.help.utils.entity_documentation import EntityDocumentation
from exactly_lib.help.utils.rendering.entity_documentation_rendering import sorted_entity_list
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator, \
    LeafArticleRendererNode
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionItemRendererNode, \
    SectionItemRendererNodeWithSubSections
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.util.textformat.structure.core import StringText


class FlatEntityListHierarchyGeneratorGetter(HtmlDocHierarchyGeneratorGetter):
    def __init__(self,
                 entity_type_identifier: str,
                 entity_doc_2_article_contents_renderer):
        self._entity_type_identifier = entity_type_identifier
        self._entity_doc_2_article_contents_renderer = entity_doc_2_article_contents_renderer

    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: list) -> SectionHierarchyGenerator:
        return HtmlDocHierarchyGeneratorForEntitiesHelp(self._entity_type_identifier,
                                                        header,
                                                        self._entity_doc_2_article_contents_renderer,
                                                        all_entity_doc_list)


class HtmlDocHierarchyGeneratorForEntitiesHelp(SectionHierarchyGenerator):
    def __init__(self,
                 entity_type_identifier: str,
                 header: str,
                 entity_2_article_contents_renderer: types.FunctionType,
                 all_entities: list):
        """
        :param entity_2_article_contents_renderer: EntityDocumentation -> ArticleContentsRenderer
        :param all_entities: [EntityDocumentation]
        """
        self.entity_type_identifier = entity_type_identifier
        self.header = header
        self.entity_2_article_contents_renderer = entity_2_article_contents_renderer
        self.all_entities = all_entities

    def renderer_node(self, target_factory: cross_ref.CustomTargetInfoFactory) -> SectionItemRendererNode:
        entity_nodes = [
            self._entity_node(entity)
            for entity in sorted_entity_list(self.all_entities)
        ]
        return SectionItemRendererNodeWithSubSections(target_factory.root(StringText(self.header)),
                                                      [],
                                                      entity_nodes)

    def _entity_node(self, entity: EntityDocumentation) -> SectionItemRendererNode:
        target_info = cross_ref.TargetInfo(entity.singular_name_text,
                                           entity.cross_reference_target())
        tags = {
            std_tags.ENTITY,
            self.entity_type_identifier,
        }
        return LeafArticleRendererNode(target_info,
                                       self.entity_2_article_contents_renderer(entity),
                                       tags=tags)
