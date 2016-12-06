from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import lists, table, document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.paragraph import Paragraph


def cross_reference_list(cross_references: list,
                         environment: RenderingEnvironment) -> ParagraphItem:
    """
    :type cross_references: [CrossReferenceTarget]
    :return: A ParagraphItem that displays a list of cross references.
    """
    return docs.simple_header_only_list([environment.cross_ref_text_constructor.apply(cross_ref)
                                         for cross_ref in cross_references],
                                        lists.ListType.ITEMIZED_LIST)


def transform_list_to_table(l: lists.HeaderContentList) -> table.Table:
    rows = []
    for item in l.items:
        assert isinstance(item, lists.HeaderContentListItem)
        header_cell = [Paragraph([item.header])]
        value_cell = item.content_paragraph_items
        rows.append([header_cell, value_cell])
    return table.Table(table.TableFormat(),
                       rows)


def append_sections_if_contents_is_non_empty(output_list_of_sections: list,
                                             section_name_and_initial_paragraphs_list: list):
    """
    Appends sections to the output list, for each section that has non-empty content.
    :param output_list_of_sections: Where sections are appended.
    :param section_name_and_initial_paragraphs_list: [(section-name, [`ParagraphItem`])]
    :return:
    """
    for name, section_contents in section_name_and_initial_paragraphs_list:
        if section_contents:
            section = doc.Section(docs._text_from_unknown(name),
                                  docs.SectionContents(section_contents, []))
            output_list_of_sections.append(section)
