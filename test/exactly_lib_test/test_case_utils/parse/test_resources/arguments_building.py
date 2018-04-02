from typing import Sequence, List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


class Arguments:
    """Instruction arguments, in the form of a first line and following lines."""

    def __init__(self,
                 first_line,
                 following_lines: Sequence = ()):
        """
        :param first_line: rendered using __str__
        :param following_lines: Every element is rendered using __str__
        """
        self.first_line = str(first_line)
        self.following_lines = list(map(str, following_lines))

    @property
    def lines(self) -> List[str]:
        return [self.first_line] + self.following_lines

    @property
    def as_single_string(self) -> str:
        return '\n'.join(self.lines)

    @property
    def as_remaining_source(self) -> ParseSource:
        return remaining_source(self.first_line,
                                self.following_lines)

    def followed_by(self,
                    arguments,
                    first_line_separator: str = ' '):
        """
        :type arguments: Arguments
        :param first_line_separator: String that separates the first line of the two arguments
        :rtype: Arguments
        """
        return Arguments(self.first_line + first_line_separator + arguments.first_line,
                         self.following_lines + arguments.following_lines)

    def followed_by_lines(self,
                          following_lines: List[str]):
        return Arguments(self.first_line,
                         tuple(self.following_lines) + tuple(following_lines))

    @property
    def num_lines(self) -> int:
        return 1 + len(self.following_lines)


class ArgumentElements:
    """Instruction arguments, in the form of a first line and following lines."""

    def __init__(self,
                 first_line: List,
                 following_lines: Sequence[List] = ()):
        """
        A line is a sequence of elements that should be separated by space and rendered by __str__
        :param first_line: Elements of the first (mandatory line
        :param following_lines: Following lines (each a sequence of elements)
        """
        self.first_line = first_line
        self.following_lines = list(following_lines)

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(render_elements_line(self.first_line),
                         [render_elements_line(line) for line in self.following_lines])

    @property
    def lines(self) -> List[List]:
        return [self.first_line] + self.following_lines

    @property
    def as_remaining_source(self) -> ParseSource:
        return self.as_arguments.as_remaining_source

    def append_to_first_line(self,
                             elements: List):
        return ArgumentElements(self.first_line + elements,
                                self.following_lines)

    def prepend_to_first_line(self,
                              elements: List):
        return ArgumentElements(elements + self.first_line,
                                self.following_lines)

    def followed_by_lines(self,
                          following_lines: List[List]):
        return ArgumentElements(self.first_line,
                                self.following_lines + following_lines)

    @property
    def num_lines(self) -> int:
        return 1 + len(self.following_lines)


def render_elements_line(line_elements: List) -> str:
    return ' '.join(map(str, line_elements))


def here_document(lines: List[str],
                  marker: str = 'EOF') -> Arguments:
    return Arguments('<<' + marker,
                     lines + [marker])
