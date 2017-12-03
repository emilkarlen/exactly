from exactly_lib.type_system.logic.matcher_base_class import Matcher


class LineMatcher(Matcher):
    """
    Matches text lines.

    A line is a tuple (line number, line contents).

    Line numbers start at 1.
    """

    def matches(self, line: tuple) -> bool:
        """
        :param line: (int, string) - (line number, line contents)
        :return: If the line matches the condition represented by the matcher
        """
        raise NotImplementedError('abstract method')
