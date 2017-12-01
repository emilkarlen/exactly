from exactly_lib.util.textformat import parse
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import table
from exactly_lib.util.textformat.structure.core import ParagraphItem, ConcreteText, StringText, CrossReferenceTarget, \
    CrossReferenceText, Text, AnchorText
from exactly_lib.util.textformat.structure.document import Section, SectionContents
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph
from exactly_lib.util.textformat.structure.table import TableCell, Table, TableFormat

SEPARATION_OF_HEADER_AND_CONTENTS = lists.Separations(1, 1)

COLON_TABLE_COLUMN_SEPARATOR = ' : '


def section(header_str_or_text,
            paragraphs: list,
            sub_sections: list = None) -> Section:
    return Section(text_from_unknown(header_str_or_text),
                   SectionContents(paragraphs,
                                   _empty_list_if_none(sub_sections)))


def section_contents(initial_paragraphs: list,
                     sub_sections: list = None) -> SectionContents:
    return SectionContents(initial_paragraphs,
                           _empty_list_if_none(sub_sections))


def simple_header_only_list(str_or_text_headers: iter,
                            list_type: lists.ListType) -> lists.HeaderContentList:
    items = [header_only_item(header) for header in str_or_text_headers]
    return lists.HeaderContentList(items,
                                   lists.Format(list_type))


def simple_list(items: iter,
                list_type: lists.ListType) -> lists.HeaderContentList:
    return lists.HeaderContentList(items,
                                   lists.Format(list_type))


def simple_list_with_space_between_elements_and_content(items: iter,
                                                        list_type: lists.ListType) -> lists.HeaderContentList:
    return lists.HeaderContentList(items,
                                   lists.Format(list_type,
                                                custom_separations=SEPARATION_OF_HEADER_AND_CONTENTS))


def list_item(header_str_or_text,
              content: list = None) -> lists.HeaderContentListItem:
    return lists.HeaderContentListItem(text_from_unknown(header_str_or_text),
                                       _empty_list_if_none(content))


def header_only_item(header_str_or_text) -> lists.HeaderContentListItem:
    return list_item(header_str_or_text, [])


def para(str_or_text) -> ParagraphItem:
    return Paragraph([text_from_unknown(str_or_text)])


def paras(str_or_text) -> list:
    """
    :type str_or_text: Either str or Text
    Singleton list of Paragraph.

    """
    return [para(str_or_text)]


def normalize_and_parse(paragraphs: str,
                        list_settings: parse.ListSettings = parse.DEFAULT_LIST_SETTINGS) -> list:
    """
    :rtype: [`ParagraphItem`]
    """
    return parse.normalize_and_parse(paragraphs, list_settings)


def text(s: str) -> ConcreteText:
    return StringText(s)


def cross_reference(title_str_or_string_text,
                    target: CrossReferenceTarget,
                    target_is_id_in_same_document: bool = True,
                    allow_rendering_of_visible_extra_target_text: bool = True) -> ConcreteText:
    title = title_str_or_string_text
    if isinstance(title_str_or_string_text, str):
        title = StringText(title_str_or_string_text)

    return CrossReferenceText(
        title,
        target,
        target_is_id_in_same_document=target_is_id_in_same_document,
        allow_rendering_of_visible_extra_target_text=allow_rendering_of_visible_extra_target_text)


def anchor_text(anchored_text: ConcreteText,
                anchor: CrossReferenceTarget = None) -> Text:
    if anchor is None:
        return anchored_text
    return AnchorText(anchored_text, anchor)


def literal_layout(s: str) -> ParagraphItem:
    return LiteralLayout(s)


def first_column_is_header_table(rows_iterable,
                                 column_separator: str = '  ') -> ParagraphItem:
    return table.Table(table.TableFormat(column_separator,
                                         first_column_is_header=True),
                       rows_iterable)


def first_row_is_header_table(rows_iterable,
                              column_separator: str = '  ') -> ParagraphItem:
    return table.Table(table.TableFormat(column_separator,
                                         first_row_is_header=True),
                       rows_iterable)


def plain_table(rows_iterable,
                column_separator: str = '  ') -> ParagraphItem:
    return table.Table(table.TableFormat(column_separator),
                       rows_iterable)


def text_from_unknown(str_or_text) -> Text:
    if isinstance(str_or_text, Text):
        return str_or_text
    else:
        return StringText(str_or_text)


def cell(paragraph_items: list) -> TableCell:
    return TableCell(paragraph_items)


def text_cell(str_or_text) -> TableCell:
    return cell(paras(str_or_text))


def single_text_cell_table(single_text_cell_rows: list) -> Table:
    return Table(TableFormat(),
                 [
                     [
                         text_cell(raw_cell)
                         for raw_cell in row
                     ]
                     for row in single_text_cell_rows
                 ])


def _empty_list_if_none(content) -> list:
    return [] if content is None else content
