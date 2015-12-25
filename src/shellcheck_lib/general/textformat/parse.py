from shellcheck_lib.general.textformat.structure.core import ParagraphItem, Text
from shellcheck_lib.general.textformat.structure.paragraph import Paragraph


def parse(normalized_lines: list) -> list:
    return _Parser(normalized_lines).apply()


def normalize_and_parse(text: str) -> list:
    lines = _space_normalize_lines(text)
    _strip_empty_lines(lines)
    return _Parser(lines).apply()


def normalize_lines(text: str) -> list:
    ret_val = _space_normalize_lines(text)
    _strip_empty_lines(ret_val)
    return ret_val


def _space_normalize_lines(text: str) -> list:
    raise NotImplementedError()


def _strip_empty_lines(space_normalized_lines: list):
    pass


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
        texts = []
        while self.has_more_lines() and not self.is_at_paragraph_separator():
            self.consume_separator()
            texts.append(self.parse_text())
        self.consume_separator()
        return Paragraph(texts)

    def parse_text(self) -> Text:
        lines = [self.consume_current_line()]
        while self.has_more_lines() and not self.is_at_separator():
            lines.append(self.consume_current_line())
        contents = ' '.join(lines)
        return Text(contents)

    def has_more_lines(self) -> bool:
        return self.lines

    def is_at_separator(self):
        return self.number_of_blank_lines() > 0

    def is_at_paragraph_separator(self) -> bool:
        return self.number_of_blank_lines() >= 2

    def consume_current_line(self) -> str:
        ret_val = self.lines[0]
        del self.lines[0]
        return ret_val

    def consume_separator(self):
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
