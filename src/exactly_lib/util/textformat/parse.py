import textwrap

from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.structure.core import ParagraphItem, Text, StringText
from exactly_lib.util.textformat.structure.literal_layout import LiteralLayout
from exactly_lib.util.textformat.structure.paragraph import Paragraph

NUM_TEXT_SEPARATOR_LINES = 1
NUM_PARAGRAPH_SEPARATOR_LINES = 2

TEXT_SEPARATOR_LINES = NUM_TEXT_SEPARATOR_LINES * ['']
PARAGRAPH_SEPARATOR_LINES = NUM_PARAGRAPH_SEPARATOR_LINES * ['']

_LITERAL_TOKEN = '```'
_LITERAL_TOKEN_LEN = len(_LITERAL_TOKEN)


def parse(normalized_lines: list) -> list:
    return _Parser(normalized_lines).apply()


def normalize_lines(text: str) -> list:
    ret_val = textwrap.dedent(text).splitlines()
    _strip_empty_lines(ret_val)
    return ret_val


def normalize_and_parse(text: str) -> list:
    normalized_lines = normalize_lines(text)
    return _Parser(normalized_lines).apply()


def _strip_empty_lines(space_normalized_lines: list):
    while space_normalized_lines and not space_normalized_lines[0]:
        del space_normalized_lines[0]
    while space_normalized_lines and not space_normalized_lines[-1]:
        del space_normalized_lines[-1]


class _Parser:
    def __init__(self,
                 lines: list):
        self.lines = lines
        self.result = []

    def apply(self) -> list:
        while self.has_more_lines():
            self.result.append(self.parse_paragraph_item())
        return self.result

    def parse_paragraph_item(self) -> ParagraphItem:
        first_line = self.lines[0]
        if self._marks_start_of_literal_block(first_line):
            return self.parse_literal_layout_from_first_marker_line()
        else:
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
        if not self.lines:
            return 0
        idx = 0
        while not self.lines[idx]:
            idx += 1
        return idx

    @staticmethod
    def _marks_start_of_literal_block(line: str):
        return line == _LITERAL_TOKEN

    @staticmethod
    def _marks_end_of_literal_block(line: str):
        return line == _LITERAL_TOKEN
