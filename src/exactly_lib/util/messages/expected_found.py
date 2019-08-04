from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer

_EXPECTED_HEADER = 'Expected : '
_FOUND_HEADER = 'Found    : '


def unexpected_lines(expected: str, found: str) -> TextRenderer:
    return text_docs.major_blocks_of_string_lines(unexpected_lines_str(expected, found))


def unexpected_lines_str(expected: str, found: str) -> str:
    return '\n'.join([
        _EXPECTED_HEADER + expected,
        _FOUND_HEADER + found,
    ])
