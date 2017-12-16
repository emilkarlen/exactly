from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


class Arguments:
    """Instruction arguments, in the form of a first line and following lines."""

    def __init__(self,
                 first_line: str,
                 following_lines: list = ()):
        self.first_line = first_line
        self.following_lines = list(following_lines)

    @property
    def lines(self) -> list:
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


def here_document(lines: list,
                  marker: str = 'EOF') -> Arguments:
    return Arguments('<<' + marker,
                     lines + [marker])
