"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
import types

from exactly_lib.help import std_tags
from exactly_lib.help.contents_structure.entity import EntityDocumentation, HtmlDocHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import sorted_entity_list
from exactly_lib.util.textformat.construction.section_hierarchy import targets
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionItemGeneratorNode, \
    SectionHierarchyGenerator, LeafArticleGeneratorNode, SectionItemGeneratorNodeWithSubSections
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

    def generator_node(self, target_factory: targets.CustomTargetInfoFactory) -> SectionItemGeneratorNode:
        entity_nodes = [
            self._entity_node(entity)
            for entity in sorted_entity_list(self.all_entities)
        ]
        return SectionItemGeneratorNodeWithSubSections(target_factory.root(StringText(self.header)),
                                                       [],
                                                       entity_nodes)

    def _entity_node(self, entity: EntityDocumentation) -> SectionItemGeneratorNode:
        target_info = targets.TargetInfo(entity.singular_name_text,
                                         entity.cross_reference_target())
        tags = {
            std_tags.ENTITY,
            self.entity_type_identifier,
        }
        return LeafArticleGeneratorNode(target_info,
                                        self.entity_2_article_contents_renderer(entity),
                                        tags=tags)
