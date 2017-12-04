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


FIRST_LINE_NUMBER = 1


def model_iter_from_file_line_iter(lines: iter) -> iter:
    """
    Gives a sequence of line matcher models, corresponding to input lines read from file.
    New lines are expected to appear only as last character of lines, or not at all, if
    last line is not ended with new line in the file.

    @:param strings: lines from an input source
    """
    return enumerate((l.rstrip('\n') for l in lines),
                     1)


def original_and_model_iter_from_file_line_iter(lines: iter) -> iter:
    """
    Gives a sequence of pairs, corresponding to each element in lines.
    (original line, line-matcher-model-for-line).

    See also docs of model_iter_from_file_line_iter.

    @:param strings: lines from an input source
    """
    return (
        (original, (line_num, original.rstrip('\n')))
        for line_num, original in enumerate(lines, 1)
    )
