from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


def append_sections_if_contents_is_non_empty(output_list_of_sections: list,
                                             section_name_and_contents_list: list):
    """
    Appends sections to the output list, for each section that has non-empty content.
    :param output_list_of_sections: Where sections are appended.
    :param section_name_and_contents_list: [(section-name, [`ParagraphItem`])]
    :return:
    """
    for name, section_contents in section_name_and_contents_list:
        if section_contents:
            section = doc.Section(docs._text_from_unknown(name),
                                  docs.SectionContents(section_contents, []))
            output_list_of_sections.append(section)
