import shlex
from typing import Dict, Any, List, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.string_formatting import StringFormatter


def source_of_lines(lines: Sequence[str]) -> ParseSource:
    return ParseSource('\n'.join(lines))


def source4(first_line: str,
            following_lines: Sequence[str] = ()) -> ParseSource:
    return ParseSource('\n'.join([first_line] + list(following_lines)))


def remaining_source(remaining_contents_of_first_line: str,
                     following_lines: Sequence[str] = ()) -> ParseSource:
    """
    :param remaining_contents_of_first_line: Part of the first line that has not been consumed.
    :return: Source with some initial content of the first line that has been consumed.
    """
    previous_content = 'previous content '
    remaining_content = '\n'.join([remaining_contents_of_first_line] + list(following_lines))
    content = previous_content + remaining_content
    ret_val = ParseSource(content)
    ret_val.consume_part_of_current_line(len(previous_content))
    return ret_val


def remaining_source_string(pre_formatted: str) -> ParseSource:
    previous_content = 'previous content '
    ret_val = ParseSource(previous_content + pre_formatted)
    ret_val.consume_part_of_current_line(len(previous_content))

    return ret_val


def remaining_source_of_abs_stx(syntax: AbstractSyntax) -> ParseSource:
    return remaining_source_string(
        syntax.tokenization().layout(LayoutSpec.of_default())
    )


def remaining_source_lines(lines: List[str]) -> ParseSource:
    """
    A variant of 'remaining_source'.
    """
    if not lines:
        raise ValueError('The source must contain at least one line')
    return remaining_source(lines[0], lines[1:])


def single_line_source(arguments: str) -> ParseSource:
    remaining_part_of_current_line = arguments
    return source4(remaining_part_of_current_line)


def argument_list_source(arguments: List[str],
                         following_lines: Sequence[str] = ()) -> ParseSource:
    return source4(' '.join(map(_quote, arguments)),
                   following_lines)


def _quote(s: str) -> str:
    if s.find(' ') != -1:
        return shlex.quote(s)
    return s


class ParseSourceBuilder:
    def __init__(self, format_map: Dict[str, Any]):
        self._string_formatter = StringFormatter(format_map)

    def format(self, template_string: str, **kwargs) -> str:
        return self._string_formatter.format(template_string, **kwargs)

    def format_dict(self, **kwargs) -> Dict[str, Any]:
        return self._string_formatter.format_dict(**kwargs)

    def single_line(self, first_line: str, **kwargs) -> ParseSource:
        return self.lines([first_line], **kwargs)

    def pre_formatted(self, pre_formatted: str) -> ParseSource:
        return remaining_source_string(self.format(pre_formatted))

    def multi_line(self,
                   first_line: str,
                   following_lines: List[str],
                   **kwargs) -> ParseSource:
        return self.lines([first_line] + following_lines, **kwargs)

    def lines(self, lines: List[str], **kwargs) -> ParseSource:
        return remaining_source_lines(self.format_lines(lines, **kwargs))

    def format_lines(self, lines: List[str], **kwargs) -> List[str]:
        return self._string_formatter.format_strings(lines, **kwargs)

    def new_with(self, **kwargs) -> 'ParseSourceBuilder':
        return ParseSourceBuilder(self._string_formatter.format_dict(**kwargs))
