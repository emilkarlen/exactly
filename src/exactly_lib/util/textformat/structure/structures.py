from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import table
from exactly_lib.util.textformat.structure.core import ParagraphItem, ConcreteText, StringText, CrossReferenceTarget, \
    CrossReferenceText, Text, AnchorText
from exactly_lib.util.textformat.structure.document import Section, SectionContents
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph

SEPARATION_OF_HEADER_AND_CONTENTS = lists.Separations(1, 1)


def section(header_str_or_text,
            paragraphs: list,
            sub_sections: list = None) -> Section:
    return Section(_text_from_unknown(header_str_or_text),
                   SectionContents(paragraphs,
                                   _empty_list_if_none(sub_sections)))


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
    return lists.HeaderContentListItem(_text_from_unknown(header_str_or_text),
                                       _empty_list_if_none(content))


def header_only_item(header_str_or_text) -> lists.HeaderContentListItem:
    return list_item(header_str_or_text, [])


def para(str_or_text) -> ParagraphItem:
    return Paragraph([_text_from_unknown(str_or_text)])


def paras(str_or_text) -> list:
    """
    :type str_or_text: Either str or Text
    Singleton list of Paragraph.

    """
    return [para(str_or_text)]


def text(s: str) -> ConcreteText:
    return StringText(s)


def cross_reference(title: str,
                    target: CrossReferenceTarget,
                    target_is_id_in_same_document: bool = True,
                    allow_rendering_of_visible_extra_target_text: bool = True) -> ConcreteText:
    return CrossReferenceText(
        title,
        target,
        target_is_id_in_same_document=target_is_id_in_same_document,
        allow_rendering_of_visible_extra_target_text=allow_rendering_of_visible_extra_target_text)


def anchor_text(anchored_text: ConcreteText,
                anchor: CrossReferenceTarget = None) -> Text:
    if anchor is None:
        return anchored_text
    return AnchorText(anchor, anchored_text)


def literal_layout(s: str) -> ParagraphItem:
    return LiteralLayout(s)


def first_column_is_header_table(rows: list,
                                 column_separator: str = '  ') -> ParagraphItem:
    return table.Table(table.TableFormat(column_separator,
                                         first_column_is_header=True),
                       rows)


def first_row_is_header_table(rows: list,
                              column_separator: str = '  ') -> ParagraphItem:
    return table.Table(table.TableFormat(column_separator,
                                         first_row_is_header=True),
                       rows)


def _text_from_unknown(str_or_text) -> Text:
    if isinstance(str_or_text, Text):
        return str_or_text
    else:
        return StringText(str_or_text)


def _empty_list_if_none(content) -> list:
    return [] if content is None else content


def cell(paragraph_items: list) -> list:
    """
    Currently, this function exists only to centralize construction of cell elements,
    to make future refactoring easy (introduction of TableCell class).
    :param paragraph_items:
    :return:
    """
    return paragraph_items
