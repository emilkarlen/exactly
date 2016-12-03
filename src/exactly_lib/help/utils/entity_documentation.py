"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""
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


class AllEntitiesListRenderer(SectionContentsRenderer):
    def __init__(self, all_entities: list):
        self.all_entities = all_entities

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents([_sorted_entities_list(self.all_entities)], [])


def sorted_entity_list(entities: list) -> list:
    return sorted(entities, key=lambda ed: ed.singular_name())


def _sorted_entities_list(entities: iter) -> ParagraphItem:
    items = [lists.HeaderContentListItem(docs.text(entity.singular_name()),
                                         docs.paras(entity.single_line_description()))
             for entity in (sorted_entity_list(entities))]
    return lists.HeaderContentList(items,
                                   lists.Format(lists.ListType.VARIABLE_LIST,
                                                custom_indent_spaces=0,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
