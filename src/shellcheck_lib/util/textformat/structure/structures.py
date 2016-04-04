from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure import lists
from shellcheck_lib.util.textformat.structure import table
from shellcheck_lib.util.textformat.structure.literal_layout import LiteralLayout
from shellcheck_lib.util.textformat.structure.paragraph import Paragraph

SEPARATION_OF_HEADER_AND_CONTENTS = lists.Separations(1, 1)


def section(header_str_or_text,
            paragraphs: list,
            sub_sections: list = None) -> doc.Section:
    return doc.Section(_text_from_unknown(header_str_or_text),
                       doc.SectionContents(paragraphs,
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


def para(str_or_text) -> core.ParagraphItem:
    return Paragraph([_text_from_unknown(str_or_text)])


def paras(str_or_text) -> list:
    """
    :type str_or_text: Either str or Text
    Singleton list of Paragraph.

    """
    return [para(str_or_text)]


def text(s: str) -> core.Text:
    return core.StringText(s)


def cross_reference(title: str,
                    target: core.CrossReferenceTarget) -> core.Text:
    return core.CrossReferenceText(title, target)


def literal_layout(s: str) -> core.ParagraphItem:
    return LiteralLayout(s)


def first_column_is_header_table(rows: list,
                                 column_separator: str = '  ') -> table.Table:
    return table.Table(table.TableFormat(column_separator),
                       rows)


def first_row_is_header_table(rows: list,
                              column_separator: str = '  ') -> table.Table:
    return table.Table(table.TableFormat(column_separator,
                                         first_row_is_header=True),
                       rows)


def _text_from_unknown(str_or_text) -> core.Text:
    if isinstance(str_or_text, core.Text):
        return str_or_text
    else:
        return core.StringText(str_or_text)


def _empty_list_if_none(content) -> list:
    return [] if content is None else content
