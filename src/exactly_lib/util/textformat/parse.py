import re
import textwrap
from typing import List, Optional, Tuple

from exactly_lib.util.str_.misc_formatting import lines_content
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

_ITEMIZED_LIST_ITEM_RE = re.compile(r' +\* ')

_ORDERED_LIST_ITEM_RE = re.compile(r' +1\. ')


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


def parse(normalized_lines: List[str],
          list_settings: ListSettings = DEFAULT_LIST_SETTINGS) -> List[ParagraphItem]:
    return _Parser(normalized_lines, list_settings).apply()


def normalize_lines(text: str) -> List[str]:
    ret_val = textwrap.dedent(text).splitlines()
    _strip_empty_lines(ret_val)
    return ret_val


def normalize_and_parse(text: str,
                        list_settings: ListSettings = DEFAULT_LIST_SETTINGS) -> List[ParagraphItem]:
    normalized_lines = normalize_lines(text)
    return _Parser(normalized_lines, list_settings).apply()


def split_and_parse(text: str,
                    list_settings: ListSettings = DEFAULT_LIST_SETTINGS) -> List[ParagraphItem]:
    lines = list(text.splitlines())
    return _Parser(lines, list_settings).apply()


def _strip_empty_lines(space_normalized_lines: List[str]):
    while space_normalized_lines and not space_normalized_lines[0]:
        del space_normalized_lines[0]
    while space_normalized_lines and not space_normalized_lines[-1]:
        del space_normalized_lines[-1]


class _Parser:
    def __init__(self,
                 lines: List[str],
                 list_settings: ListSettings):
        self.list_settings = list_settings
        self.lines = lines
        self.result = []

    def apply(self) -> List[ParagraphItem]:
        self.consume_separator_lines()
        while self.has_more_lines():
            self.result.append(self.parse_paragraph_item())
        return self.result

    def parse_paragraph_item(self) -> ParagraphItem:
        first_line = self.lines[0]
        is_literal, class_ = self._marks_start_of_literal_block(first_line)
        if is_literal:
            return self.parse_literal_layout_from_first_marker_line(class_)
        list_paragraph = self._try_parse_list()
        if list_paragraph:
            return list_paragraph
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

    def parse_literal_layout_from_first_marker_line(self, class_: str) -> LiteralLayout:
        del self.lines[0]
        lines = []
        while True:
            if not self.has_more_lines():
                raise ValueError('Reached end of file before end marker found: ("%s")' % _LITERAL_TOKEN)
            first_line = self.lines[0]
            if self._marks_end_of_literal_block(first_line):
                del self.lines[0]
                self.consume_separator_lines()
                return LiteralLayout(lines_content(lines), class_)
            if first_line and first_line[0] == '\\':
                self.lines[0] = first_line[1:]
            lines.append(self.lines[0])
            del self.lines[0]

    def _try_parse_list(self) -> Optional[lists.HeaderContentList]:
        first_line = self.lines[0]
        match = _ITEMIZED_LIST_ITEM_RE.match(first_line)
        if match:
            return self.parse_list_from_first_item_line(match.group(0),
                                                        lists.ListType.ITEMIZED_LIST)

        match = _ORDERED_LIST_ITEM_RE.match(first_line)
        if match:
            return self.parse_list_from_first_item_line(match.group(0),
                                                        lists.ListType.ORDERED_LIST)

        return None

    def parse_list_from_first_item_line(self,
                                        item_line_prefix: str,
                                        list_type: lists.ListType) -> lists.HeaderContentList:
        items = [self.parse_list_item_from_item_line(self.consume_current_line(),
                                                     item_line_prefix)]
        while self.has_more_lines() and self.lines[0].startswith(item_line_prefix):
            next_item = self.parse_list_item_from_item_line(self.consume_current_line(),
                                                            item_line_prefix)
            items.append(next_item)
        return lists.HeaderContentList(items, self._list_format(list_type))

    def _list_format(self, list_type: lists.ListType) -> lists.Format:
        return lists.Format(list_type,
                            custom_indent_spaces=self.list_settings.custom_indent_spaces,
                            custom_separations=self.list_settings.custom_separations)

    def parse_list_item_from_item_line(self,
                                       first_item_header_line: str,
                                       item_line_prefix: str) -> lists.HeaderContentListItem:
        item_line_prefix_len = len(item_line_prefix)
        header = first_item_header_line[item_line_prefix_len:].strip()

        content_paragraph_items = self.parse_list_content_paragraph_items(item_line_prefix_len)
        return docs.list_item(StringText(header), content_paragraph_items)

    def parse_list_content_paragraph_items(self, item_contents_indent_len: int) -> List[ParagraphItem]:
        normalized_item_contents_lines = self.consume_and_normalize_indented_lines(item_contents_indent_len)
        return _Parser(normalized_item_contents_lines,
                       self.list_settings).apply()

    def consume_and_normalize_indented_lines(self, indent_len: int) -> List[str]:
        ret_val = []
        while self.lines and self.lines[0][:indent_len].lstrip(' ') == '':
            line = self.consume_current_line()
            if len(line) >= indent_len:
                line = line[indent_len:]
            else:
                line = ''
            ret_val.append(line)
        _strip_empty_lines(ret_val)
        return ret_val

    def parse_text(self) -> Text:
        lines = [self.consume_current_line().strip()]
        while self.has_more_lines() and not self.is_at_separator():
            lines.append(self.consume_current_line().strip())
        contents = ' '.join(lines)
        return StringText(contents)

    def has_more_lines(self) -> bool:
        return bool(self.lines)

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
    def _marks_start_of_literal_block(line: str) -> Tuple[bool, Optional[str]]:
        if line[:len(_LITERAL_TOKEN)] != _LITERAL_TOKEN:
            return False, None
        after = line[len(_LITERAL_TOKEN):]
        if after == '':
            return True, None
        elif after[0] == ':':
            return True, after[1:].strip()
        else:
            return False, None

    @staticmethod
    def _marks_end_of_literal_block(line: str) -> bool:
        return line == _LITERAL_TOKEN
