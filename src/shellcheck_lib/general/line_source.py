import os
import pathlib


class Line(tuple):
    def __new__(cls,
                line_number: int,
                text: str):
        return tuple.__new__(cls, (line_number, text))

    @property
    def line_number(self) -> int:
        return self[0]

    @property
    def text(self) -> str:
        return self[1]


class LineSequence:
    """
    One or more consecutive lines.
    """

    def __init__(self,
                 first_line_number: int,
                 lines: tuple):
        """
        :param first_line_number: Line number of first line in the sequence.
        :param lines: Non-empty list of individual lines, without ending line-separator.
        """
        self._first_line_number = first_line_number
        self._lines = lines

    @property
    def first_line_number(self) -> int:
        return self._first_line_number

    @property
    def lines(self) -> tuple:
        """
        All lines (at least one). No line ends with the line-separator.
        """
        return self._lines

    @property
    def first_line(self) -> Line:
        return Line(self._first_line_number, self._lines[0])

    @property
    def text(self) -> str:
        """
        All lines, separated by line-separator, but not ending with one.
        """
        return os.linesep.join(self._lines)


def new_ls_from_line(line: Line) -> LineSequence:
    return LineSequence(line.line_number,
                        (line.text,))


class LineSequenceSource:
    def has_next(self) -> bool:
        raise NotImplementedError()

    def next_line(self) -> str:
        """
        The next line without line-separator at end.
        :return None iff end-of-file has been reached.
        """
        raise NotImplementedError()

    def return_line(self, line: str):
        raise NotImplementedError()


class LineSequenceBuilder:
    def __init__(self,
                 source: LineSequenceSource,
                 first_line_number: int,
                 first_line: str):
        self._source = source
        self._first_line_number = first_line_number
        self._lines = [first_line]

    def build(self) -> LineSequence:
        return LineSequence(self._first_line_number,
                            tuple(self._lines))

    @property
    def first_line(self) -> Line:
        return Line(self._first_line_number, self._lines[0])

    @property
    def lines(self) -> list:
        return self._lines

    @property
    def text(self) -> str:
        """
        :return: All current lines in same for as the text in the built LineSequence.
        """
        return self.build().text

    def has_next(self) -> bool:
        return self._source.has_next()

    def next_line(self) -> str:
        """
        The next line without line-separator at end.
        The line is added to the list of lines that this builder stores.
        :return The line. None iff end-of-file has been reached.
        """
        if self._source.has_next():
            next_line = self._source.next_line()
            self._lines.append(next_line)
            return next_line
        else:
            return None

    def return_line(self):
        """
        Returns the last line given by next_line to the source that backs
        this object, and do not include it in the LineSequence that is built.

        Can only return lines that have been retrieved by next_line.

        :raises ValueError If called more times than next_line.
        """
        if len(self._lines) == 1:
            raise ValueError('There is no line that can be returned')
        self._source.return_line(self._lines.pop())


class LineSource:
    """
    Iterable over a sequence of Line:s.

    Line numbers start at 1.
    """

    def __iter__(self):
        raise NotImplementedError()


def new_for_string(contents: str) -> LineSource:
    return _LineSourceForString(contents)


def new_for_file(path: pathlib.Path) -> LineSource:
    with path.open() as fo:
        contents = fo.read()
    return new_for_string(contents)


class _LineSourceForString(LineSource):
    def __init__(self, contents: str):
        self._lines = enumerate(contents.splitlines(),
                                start=1)

    def __iter__(self):
        for n, s in self._lines:
            yield Line(n, s)
