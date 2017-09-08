from exactly_lib.help.utils.entity_documentation import EntityDocumentation
from exactly_lib.help.utils.rendering.section_contents_renderer import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc, lists, structures as docs
from exactly_lib.util.textformat.structure.structures import SEPARATION_OF_HEADER_AND_CONTENTS
from exactly_lib.util.textformat.utils import transform_list_to_table


def sorted_entity_list(entities: list) -> list:
    return sorted(entities, key=lambda ed: ed.singular_name())


def entity_doc_list_renderer_as_flat_list_of_single_line_description(entity_doc_list: list) -> SectionContentsRenderer:
    return AllEntitiesListRenderer(single_line_description_as_summary_paragraphs,
                                   entity_doc_list)


def single_line_description_as_summary_paragraphs(entity_doc: EntityDocumentation) -> list:
    return docs.paras(entity_doc.single_line_description())


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
        return doc.SectionContents([transform_list_to_table(self._sorted_entities_list(self.all_entities))], [])

    def _sorted_entities_list(self, entities: iter) -> lists.HeaderContentList:
        items = [lists.HeaderContentListItem(docs.text(entity.singular_name()),
                                             self.entity_2_summary_paragraphs(entity))
                 for entity in (sorted_entity_list(entities))]
        return lists.HeaderContentList(items,
                                       lists.Format(lists.ListType.VARIABLE_LIST,
                                                    custom_indent_spaces=0,
                                                    custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))
