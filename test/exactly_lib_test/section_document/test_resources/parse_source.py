import shlex

from exactly_lib.section_document.parse_source import ParseSource


def source3(lines: list) -> ParseSource:
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
