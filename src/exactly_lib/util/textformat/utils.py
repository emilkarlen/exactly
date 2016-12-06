from exactly_lib.util.textformat.structure import lists, table, structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents, Section
from exactly_lib.util.textformat.structure.paragraph import Paragraph


def append_section_if_contents_is_non_empty(output_list_of_sections: list,
                                            section_title_str_or_text,
                                            initial_paragraphs_or_section_contents: SectionContents):
    section_contents = initial_paragraphs_or_section_contents
    if isinstance(initial_paragraphs_or_section_contents, list):
        section_contents = SectionContents(initial_paragraphs_or_section_contents)
    if not section_contents.is_empty:
        output_list_of_sections.append(Section(docs.text_from_unknown(section_title_str_or_text),
                                               section_contents))


def append_sections_if_contents_is_non_empty(output_list_of_sections: list,
                                             section_name__initial_paragraphs_list_or_section_contents: list):
    """
    Appends sections to the output list, for each section that has non-empty content.
    :param output_list_of_sections: Where sections are appended.
    :param section_name__initial_paragraphs_list_or_section_contents:
    [(section-name, SectionContents|[`ParagraphItem`])]
    :return:
    """
    for name, section_contents in section_name__initial_paragraphs_list_or_section_contents:
        append_section_if_contents_is_non_empty(output_list_of_sections, name, section_contents)


def transform_list_to_table(l: lists.HeaderContentList) -> table.Table:
    rows = []
    for item in l.items:
        assert isinstance(item, lists.HeaderContentListItem)
        header_cell = [Paragraph([item.header])]
        value_cell = item.content_paragraph_items
        rows.append([header_cell, value_cell])
    return table.Table(table.TableFormat(),
                       rows)
