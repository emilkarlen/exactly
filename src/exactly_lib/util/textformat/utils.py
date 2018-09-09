from typing import List, Union, Tuple

from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists, table, structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.structures import cell

InitialParagraphsOrSectionContents = Union[doc.SectionContents, List[ParagraphItem]]


def append_section_if_contents_is_non_empty(
        output_list_of_sections: List[doc.SectionItem],
        section_title_str_or_text,
        initial_paragraphs_or_section_contents: InitialParagraphsOrSectionContents):
    section_contents = initial_paragraphs_or_section_contents
    if isinstance(initial_paragraphs_or_section_contents, list):
        section_contents = doc.SectionContents(initial_paragraphs_or_section_contents)
    if not section_contents.is_empty:
        output_list_of_sections.append(doc.Section(docs.text_from_unknown(section_title_str_or_text),
                                                   section_contents))


def append_sections_if_contents_is_non_empty(
        output_list_of_sections: List[doc.SectionItem],
        section_name__contents: List[Tuple[str, InitialParagraphsOrSectionContents]]):
    """
    Appends sections to the output list, for each section that has non-empty content.
    """
    for name, section_contents in section_name__contents:
        append_section_if_contents_is_non_empty(output_list_of_sections, name, section_contents)


def transform_list_to_table(l: lists.HeaderContentList) -> table.Table:
    rows = []
    for item in l.items:
        assert isinstance(item, lists.HeaderContentListItem)
        header_cell = cell([Paragraph([item.header])])
        value_cell = cell(item.content_paragraph_items)
        rows.append([header_cell, value_cell])
    return table.Table(table.TableFormat(),
                       rows)


def section_item_contents_as_section_contents(section_item: doc.SectionItem) -> doc.SectionContents:
    return _ContentsAsSectionContentsHelper().visit(section_item)


class _ContentsAsSectionContentsHelper(doc.SectionItemVisitor):
    def __init__(self):
        pass

    def visit_section(self, section: doc.Section) -> doc.SectionContents:
        return section.contents

    def visit_article(self, article: doc.Article) -> doc.SectionContents:
        return article.contents.combined_as_section_contents
