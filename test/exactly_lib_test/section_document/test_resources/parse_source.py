import shlex
from typing import Dict, Any, List

from exactly_lib.section_document.parse_source import ParseSource


def source_of_lines(lines: list) -> ParseSource:
    return ParseSource('\n'.join(lines))


def source4(first_line: str,
            following_lines: list = ()) -> ParseSource:
    return ParseSource('\n'.join([first_line] + list(following_lines)))


def remaining_source(remaining_contents_of_first_line: str,
                     following_lines: list = ()) -> ParseSource:
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


def remaining_source_lines(lines: list) -> ParseSource:
    """
    A variant of 'remaining_source'.
    """
    if not lines:
        raise ValueError('The source must contain at least one line')
    return remaining_source(lines[0], lines[1:])


def single_line_source(arguments: str) -> ParseSource:
    remaining_part_of_current_line = arguments
    return source4(remaining_part_of_current_line)


def argument_list_source(arguments: list,
                         following_lines: iter = ()) -> ParseSource:
    return source4(' '.join(map(_quote, arguments)),
                   following_lines)


def _quote(s: str) -> str:
    if s.find(' ') != -1:
        return shlex.quote(s)
    return s


class ParseSourceBuilder:
    def __init__(self, format_map: Dict[str, Any]):
        self._format_map = format_map

    def format(self, template_string: str, **kwargs) -> str:
        return template_string.format_map(self.format_dict(**kwargs))

    def format_dict(self, **kwargs) -> Dict[str, Any]:
        if kwargs:
            return dict(self._format_map, **kwargs)
        else:
            return self._format_map

    def single_line(self, first_line: str, **kwargs) -> ParseSource:
        return self.lines([first_line], **kwargs)

    def multi_line(self,
                   first_line: str,
                   following_lines: List[str],
                   **kwargs) -> ParseSource:
        return self.lines([first_line] + following_lines, **kwargs)

    def lines(self, lines: List[str], **kwargs) -> ParseSource:
        return remaining_source_lines(self.format_lines(lines, **kwargs))

    def format_lines(self, lines: List[str], **kwargs) -> List[str]:
        format_map = self.format_dict(**kwargs)
        return [line.format_map(format_map)
                for line in lines]

    def new_with(self, **kwargs):
        return ParseSourceBuilder(dict(self._format_map, **kwargs))
