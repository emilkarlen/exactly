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
    raise NotImplementedError()


class _LineSourceForString(LineSource):
    def __init__(self, contents: str):
        self._lines = enumerate(contents.splitlines(),
                                start=1)

    def __iter__(self):
        for n, s in self._lines:
            yield Line(n, s)
