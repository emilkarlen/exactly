from typing import Sequence, List

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.arguments_building import Stringable


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

    @staticmethod
    def empty() -> 'Arguments':
        return Arguments('', ())

    @property
    def is_empty(self) -> bool:
        return not self.first_line and not self.following_lines

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
                    arguments: 'Arguments',
                    first_line_separator: str = ' ') -> 'Arguments':
        """
        :param first_line_separator: String that separates the first line of the two arguments
        """
        return Arguments(self.first_line + first_line_separator + arguments.first_line,
                         self.following_lines + arguments.following_lines)

    def last_line_followed_by(self,
                              arguments,
                              first_line_separator: str = ' '):
        """
        Appends arguments to the last line

        :type arguments: Arguments
        :param first_line_separator: String that separates the first line of the two arguments
        :rtype: Arguments
        """
        if self.following_lines:
            return Arguments(self.first_line,
                             self.following_lines[:-1] +
                             [self.following_lines[-1] + first_line_separator + arguments.first_line] +
                             arguments.following_lines)
        else:
            return self.followed_by(arguments, first_line_separator)

    def followed_by_lines(self,
                          following_lines: List[str]):
        return Arguments(self.first_line,
                         tuple(self.following_lines) + tuple(following_lines))

    @property
    def num_lines(self) -> int:
        return 1 + len(self.following_lines)

    def prepend_to_first_line(self, prefix: str):
        return Arguments(prefix + self.first_line,
                         self.following_lines)


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
        self._first_line = first_line
        self._following_lines = list(following_lines)

    @staticmethod
    def new_with_following_lines_as_single_elements(first_line: List[Stringable],
                                                    following_lines: List[Stringable]):
        return ArgumentElements(first_line,
                                [[line] for line in following_lines])

    @property
    def first_line(self) -> List[Stringable]:
        return self._first_line

    @property
    def following_lines(self) -> List[List[Stringable]]:
        return self._following_lines

    @property
    def as_arguments(self) -> Arguments:
        return Arguments(render_elements_line(self.first_line),
                         [render_elements_line(line) for line in self.following_lines])

    @property
    def lines(self) -> List[List]:
        return [self.first_line] + self.following_lines

    @property
    def all_lines(self) -> List[List[Stringable]]:
        return [self.first_line] + self.following_lines

    @property
    def as_remaining_source(self) -> ParseSource:
        return self.as_arguments.as_remaining_source

    def append_to_first_line(self, elements: List):
        return ArgumentElements(self.first_line + elements,
                                self.following_lines)

    def with_first_line_preceded_by(self, elements: List):
        return ArgumentElements(elements + self.first_line,
                                self.following_lines)

    def prepend_to_first_line(self, elements: List):
        return ArgumentElements(elements + self.first_line,
                                self.following_lines)

    def followed_by_lines(self,
                          following_lines: List[List]):
        return ArgumentElements(self.first_line,
                                self.following_lines + following_lines)

    def append_to_first_and_following_lines(self, argument_elements):
        assert isinstance(argument_elements, ArgumentElements)
        return ArgumentElements(self.first_line + argument_elements.first_line,
                                self.following_lines + argument_elements.following_lines)

    def followed_by(self,
                    argument_elements,
                    first_line_separator: Sequence = ()):
        """
        :type argument_elements: ArgumentElements
        :param first_line_separator: String that separates the first line of the two arguments
        :rtype: ArgumentElements
        """
        return ArgumentElements(self.first_line + list(first_line_separator) + argument_elements.first_line,
                                self.following_lines + argument_elements.following_lines)

    def last_line_followed_by(self,
                              argument_elements,
                              first_line_separator: Sequence = ()):
        """
        :type argument_elements: ArgumentElements
        :param first_line_separator: String that separates the first line of the two arguments
        :rtype: ArgumentElements
        """
        if not self.following_lines:
            return self.followed_by(argument_elements, first_line_separator)
        else:
            return ArgumentElements(self.first_line,
                                    self.following_lines[:-1] +
                                    [self.following_lines[-1] + argument_elements.first_line] +
                                    argument_elements.following_lines)

    @property
    def num_lines(self) -> int:
        return 1 + len(self.following_lines)


def elements(elems: List[Stringable]) -> ArgumentElements:
    return ArgumentElements(elems)


def empty() -> ArgumentElements:
    return ArgumentElements([])


def render_elements_line(line_elements: List) -> str:
    return ' '.join(map(str, line_elements))


def string_as_elements(string: str) -> ArgumentElements:
    return ArgumentElements([string])


def here_document(lines: List[str],
                  marker: str = 'EOF') -> Arguments:
    return Arguments('<<' + marker,
                     lines + [marker])


def here_document_as_elements(lines: List[str],
                              marker: str = 'EOF') -> ArgumentElements:
    return ArgumentElements.new_with_following_lines_as_single_elements(['<<' + marker],
                                                                        lines + [marker])
