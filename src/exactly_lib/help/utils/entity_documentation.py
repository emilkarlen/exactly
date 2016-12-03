"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""

from exactly_lib.help.cross_reference_id import CrossReferenceId
from exactly_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text, ParagraphItem
from exactly_lib.util.textformat.structure.structures import SEPARATION_OF_HEADER_AND_CONTENTS


class EntityDocumentation:
    """
    Base class for documentation of "entities" with a name and single-line-description.
    """

    def singular_name(self) -> str:
        """
        Name of the entity in singular.
        """
        raise NotImplementedError()

    def single_line_description(self) -> Text:
        """
        A short description of the entity.
        """
        raise NotImplementedError()

    def cross_reference_target(self) -> CrossReferenceId:
        raise NotImplementedError()


class EntitiesHelp(tuple):
    def __new__(cls,
                entity_type_name: str,
                entities: iter):
        """
        :type entities: [`EntityDocumentation`]
        """
        return tuple.__new__(cls, (entity_type_name, list(entities)))

    @property
    def entity_type_name(self) -> str:
        """
        Name of entity.
        """
        return self[0]

    @property
    def all_entities(self) -> list:
        """
        :type: [`EntityDocumentation`]
        """
        return self[1]

    def lookup_by_name_in_singular(self, entity_name: str) -> EntityDocumentation:
        matches = list(filter(lambda e: e.singular_name() == entity_name, self.all_entities))
        if not matches:
            raise KeyError('Not a ' + self.entity_type_name + ': ' + entity_name)
        return matches[0]


def sorted_entity_list(entities: list) -> list:
    return sorted(entities, key=lambda ed: ed.singular_name())


class AllEntitiesListRenderer(SectionContentsRenderer):
    def __init__(self,
                 entity_2_summary_paragraphs,
                 all_entities: list):
        """
        :param entity_2_summary_paragraphs: EntityDocumentation -> [ParagraphItem]
        """
        self.entity_2_summary_paragraphs = entity_2_summary_paragraphs
        self.all_entities = all_entities

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([self._sorted_entities_list(self.all_entities)], [])

    def _sorted_entities_list(self, entities: iter) -> ParagraphItem:
        items = [lists.HeaderContentListItem(docs.text(entity.singular_name()),
                                             self.entity_2_summary_paragraphs(entity))
                 for entity in (sorted_entity_list(entities))]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0,
                                                    custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
