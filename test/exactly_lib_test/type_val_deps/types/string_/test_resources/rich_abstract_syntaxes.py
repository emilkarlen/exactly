from typing import Sequence

from exactly_lib.impls.types.string_ import syntax_elements as string_se
from exactly_lib.util.str_ import misc_formatting
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string_.test_resources import here_doc
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.rich_abstract_syntax import RichStringAbsStx


class PlainStringAbsStx(RichStringAbsStx):
    def __init__(self, string: StringAbsStx):
        self._string = string

    @property
    def spans_whole_line(self) -> bool:
        return False

    def tokenization(self) -> TokenSequence:
        return self._string.tokenization()


class TextUntilEndOfLineAbsStx(RichStringAbsStx):
    def __init__(self, value: str):
        self.value = value
        if '\n' in value:
            raise ValueError('Value contains new-line: ' + repr(value))

    @property
    def spans_whole_line(self) -> bool:
        return True

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([self._doc_token(), layout.NEW_LINE_IF_NOT_FIRST_OR_LAST])

    def _doc_token(self) -> str:
        return ' '.join([
            string_se.TEXT_UNTIL_EOL_MARKER,
            self.value,
        ])


class HereDocAbsStx(RichStringAbsStx):
    def __init__(self,
                 new_line_ended_value: str,
                 marker: str = 'EOF',
                 ):
        self.value = new_line_ended_value
        self.marker = marker
        if not new_line_ended_value or new_line_ended_value[-1] != '\n':
            raise ValueError('Invalid contents: ' + repr(new_line_ended_value))

    @property
    def spans_whole_line(self) -> bool:
        return True

    @staticmethod
    def of_lines__wo_new_lines(lines: Sequence[str],
                               marker: str = 'EOF',
                               ) -> 'HereDocAbsStx':
        return HereDocAbsStx(misc_formatting.lines_content(lines), marker)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([self._doc_token(), layout.NEW_LINE_IF_NOT_FIRST_OR_LAST])

    def _doc_token(self) -> str:
        return ''.join([
            here_doc.here_doc_start_token(self.marker),
            '\n',
            self.value,
            self.marker,
        ])
