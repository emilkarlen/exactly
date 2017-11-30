import re
import textwrap

from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text, StringText
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph

NUM_TEXT_SEPARATOR_LINES = 1
NUM_PARAGRAPH_SEPARATOR_LINES = 2

TEXT_SEPARATOR_LINES = NUM_TEXT_SEPARATOR_LINES * ['']
PARAGRAPH_SEPARATOR_LINES = NUM_PARAGRAPH_SEPARATOR_LINES * ['']

_LITERAL_TOKEN = '```'
_LITERAL_TOKEN_LEN = len(_LITERAL_TOKEN)

_ITEMIZED_LIST_ITEM_RE = re.compile(r'( +)\* +')


class ListSettings(tuple):
    def __new__(cls,
                custom_indent_spaces: int,
                custom_separations: lists.Separations):
        return tuple.__new__(cls, (custom_indent_spaces,
                                   custom_separations))

    @property
    def custom_indent_spaces(self) -> int:
        return self[0]

    @property
    def custom_separations(self) -> lists.Separations:
        return self[1]


DEFAULT_LIST_SETTINGS = ListSettings(None, lists.Separations(1, 1))


def parse(normalized_lines: list,
          list_settings: ListSettings = DEFAULT_LIST_SETTINGS) -> list:
    return _Parser(normalized_lines, list_settings).apply()


def normalize_lines(text: str) -> list:
    ret_val = textwrap.dedent(text).splitlines()
    _strip_empty_lines(ret_val)
    return ret_val


def normalize_and_parse(text: str,
                        list_settings: ListSettings = DEFAULT_LIST_SETTINGS) -> list:
    """
    :rtype: [`ParagraphItem`]
    """
    normalized_lines = normalize_lines(text)
    return _Parser(normalized_lines, list_settings).apply()


def _strip_empty_lines(space_normalized_lines: list):
    while space_normalized_lines and not space_normalized_lines[0]:
        del space_normalized_lines[0]
    while space_normalized_lines and not space_normalized_lines[-1]:
        del space_normalized_lines[-1]


class _Parser:
    def __init__(self,
                 lines: list,
                 list_settings: ListSettings):
        self.itemized_list_format = lists.Format(lists.ListType.ITEMIZED_LIST,
                                                 custom_indent_spaces=list_settings.custom_indent_spaces,
                                                 custom_separations=list_settings.custom_separations)
        self.lines = lines
        self.result = []

    def apply(self) -> list:
        self.consume_separator_lines()
        while self.has_more_lines():
            self.result.append(self.parse_paragraph_item())
        return self.result

    def parse_paragraph_item(self) -> ParagraphItem:
        first_line = self.lines[0]
        if self._marks_start_of_literal_block(first_line):
            return self.parse_literal_layout_from_first_marker_line()
        list_level = _is_itemized_list_item_level(first_line)
        if list_level is not None:
            return self.parse_itemized_list_from_first_item_line(list_level)
        if first_line[0] == '\\':
            self.lines[0] = first_line[1:]
        return self.parse_paragraph()

    def parse_paragraph(self) -> Paragraph:
        texts = []
        while self.has_more_lines() and not self.is_at_paragraph_separator():
            self.consume_separator_lines()
            texts.append(self.parse_text())
        self.consume_separator_lines()
        return Paragraph(texts)

    def parse_literal_layout_from_first_marker_line(self) -> LiteralLayout:
        del self.lines[0]
        lines = []
        while True:
            if not self.has_more_lines():
                raise ValueError('Reached end of file before end marker found: ("%s")' % _LITERAL_TOKEN)
            first_line = self.lines[0]
            if self._marks_end_of_literal_block(first_line):
                del self.lines[0]
                self.consume_separator_lines()
                return LiteralLayout(lines_content(lines))
            if first_line and first_line[0] == '\\':
                self.lines[0] = first_line[1:]
            lines.append(self.lines[0])
            del self.lines[0]

    def parse_itemized_list_from_first_item_line(self, level: int) -> lists.HeaderContentList:
        item_line_prefix = ' ' * level + '* '
        items = [self.parse_list_item_from_item_line(self.consume_current_line(),
                                                     level,
                                                     item_line_prefix)]
        while self.has_more_lines():
            num_blank_lines = self.number_of_blank_lines()
            if num_blank_lines > 1:
                self.consume_separator_lines()
                break
            if num_blank_lines == 1:
                self.consume_current_line()
            if not self.has_more_lines():
                break
            current_line = self.consume_current_line()
            if not current_line.startswith(item_line_prefix):
                break
            next_item = self.parse_list_item_from_item_line(current_line, level, item_line_prefix)
            items.append(next_item)
        return lists.HeaderContentList(items, self.itemized_list_format)

    def parse_list_item_from_item_line(self, current_line: str,
                                       level: int,
                                       item_line_prefix: str) -> lists.HeaderContentListItem:
        item_line_prefix_len = len(item_line_prefix)
        header = current_line[item_line_prefix_len:].strip()

        content_paragraph_items = self.parse_list_content_paragraph_items(len(item_line_prefix))
        return docs.list_item(StringText(header), content_paragraph_items)

    def parse_list_content_paragraph_items(self, item_contents_indent_len: int) -> list:
        texts = self.parse_list_content_texts(item_contents_indent_len)
        if texts:
            return [Paragraph(texts)]
        else:
            return []

    def parse_list_content_texts(self, item_contents_indent_len: int) -> list:
        ret_val = []
        while self.has_more_lines():
            num_blank_lines = self.number_of_blank_lines()
            if num_blank_lines > 1:
                break
            if num_blank_lines == 1:
                self.consume_current_line()
            if not self.has_more_lines():
                break
            non_empty_line = self.lines[0]
            assert isinstance(non_empty_line, str)
            if _is_itemized_list_item_level(non_empty_line):
                return ret_val
            if not non_empty_line[:item_contents_indent_len].isspace():
                break
            ret_val.append(self.parse_list_item_text(item_contents_indent_len))
        return ret_val

    def parse_list_item_text(self, item_line_prefix_len: int) -> Text:
        lines = [self.consume_current_line().strip()]
        while self.has_more_lines() and not self.is_at_separator():
            non_empty_line = self.lines[0]
            assert isinstance(non_empty_line, str)
            if not non_empty_line[:item_line_prefix_len].isspace():
                break
            lines.append(self.consume_current_line().strip())
        contents = ' '.join(lines)
        return StringText(contents)

    def parse_text(self) -> Text:
        lines = [self.consume_current_line().strip()]
        while self.has_more_lines() and not self.is_at_separator():
            lines.append(self.consume_current_line().strip())
        contents = ' '.join(lines)
        return StringText(contents)

    def has_more_lines(self) -> bool:
        return self.lines

    def is_at_separator(self):
        return self.number_of_blank_lines() > 0

    def is_at_paragraph_separator(self) -> bool:
        return self.number_of_blank_lines() >= NUM_PARAGRAPH_SEPARATOR_LINES

    def consume_current_line(self) -> str:
        ret_val = self.lines[0]
        del self.lines[0]
        return ret_val

    def consume_separator_lines(self):
        if self.lines:
            while not self.lines[0]:
                del self.lines[0]

    def number_of_blank_lines(self):
        idx = 0
        num_lines_left = len(self.lines)
        while idx < num_lines_left and not self.lines[idx]:
            idx += 1
        return idx

    @staticmethod
    def _marks_start_of_literal_block(line: str) -> bool:
        return line == _LITERAL_TOKEN

    @staticmethod
    def _marks_end_of_literal_block(line: str) -> bool:
        return line == _LITERAL_TOKEN


def _is_itemized_list_item_level(line: str) -> int:
    match = _ITEMIZED_LIST_ITEM_RE.match(line)
    if match:
        return len(match.group(1))
    else:
        return None
