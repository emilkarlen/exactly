"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
from typing import List, Callable

from exactly_lib.help import std_tags
from exactly_lib.help.contents_structure.entity import EntityDocumentation, HtmlDocHierarchyGeneratorGetter
from exactly_lib.help.render.entity_docs import sorted_entity_list
from exactly_lib.util.textformat.constructor import paragraphs
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator


class FlatEntityListHierarchyGeneratorGetter(HtmlDocHierarchyGeneratorGetter):
    def __init__(self,
                 entity_type_identifier: str,
                 mk_article_constructor: Callable[[EntityDocumentation], ArticleContentsConstructor]):
        self._entity_type_identifier = entity_type_identifier
        self._mk_article_constructor = mk_article_constructor

    def get_hierarchy_generator(self,
                                header: str,
                                all_entity_doc_list: List[EntityDocumentation]) -> SectionHierarchyGenerator:
        return entity_list_hierarchy(
            self._entity_type_identifier,
            self._mk_article_constructor,
            header,
            all_entity_doc_list
        )


def entity_list_hierarchy(entity_type_identifier: str,
                          mk_article_constructor: Callable[[EntityDocumentation], ArticleContentsConstructor],
                          header: str,
                          entities: List[EntityDocumentation]
                          ) -> SectionHierarchyGenerator:
    def entity_node(entity: EntityDocumentation) -> SectionHierarchyGenerator:
        additional_tags = {
            std_tags.ENTITY,
            entity_type_identifier,
        }
        return h.with_fixed_root_target(
            entity.cross_reference_target(),
            h.leaf_article(
                entity.singular_name_text,
                mk_article_constructor(entity),
                additional_tags)
        )

    return h.hierarchy(
        header,
        paragraphs.empty(),
        [
            entity_node(entity)
            for entity in sorted_entity_list(entities)
        ]
    )
