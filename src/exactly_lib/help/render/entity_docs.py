from typing import Callable, List, Iterable

from exactly_lib.help.contents_structure.entity import EntityDocumentation, CliListConstructorGetter
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc, lists, structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import SEPARATION_OF_HEADER_AND_CONTENTS
from exactly_lib.util.textformat.utils import transform_list_to_table


def sorted_entity_list(entities: Iterable[EntityDocumentation]) -> List[EntityDocumentation]:
    return sorted(entities, key=lambda ed: ed.singular_name())


def entity_doc_list_renderer_as_flat_list_of_single_line_description(
        entity_doc_list: Iterable[EntityDocumentation]) -> SectionContentsConstructor:
    return EntitiesListConstructor(single_line_description_as_summary_paragraphs,
                                   entity_doc_list)


class FlatListConstructorWithSingleLineDescriptionGetter(CliListConstructorGetter):
    def get_constructor(self, all_entity_doc_list: Iterable[EntityDocumentation]) -> SectionContentsConstructor:
        return EntitiesListConstructor(single_line_description_as_summary_paragraphs,
                                       all_entity_doc_list)


def single_line_description_as_summary_paragraphs(entity_doc: EntityDocumentation) -> List[ParagraphItem]:
    return docs.paras(entity_doc.single_line_description())


class EntitiesListConstructor(SectionContentsConstructor):
    def __init__(self,
                 entity_2_summary_paragraphs: Callable[[EntityDocumentation], List[ParagraphItem]],
                 all_entities: Iterable[EntityDocumentation]):
        self.entity_2_summary_paragraphs = entity_2_summary_paragraphs
        self.all_entities = all_entities

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return doc.SectionContents([transform_list_to_table(self._sorted_entities_list(self.all_entities))], [])

    def _sorted_entities_list(self, entities: Iterable[EntityDocumentation]) -> lists.HeaderContentList:
        items = [docs.list_item(entity.singular_name(),
                                self.entity_2_summary_paragraphs(entity))
                 for entity in (sorted_entity_list(entities))]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0,
                                                    custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
