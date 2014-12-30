__author__ = 'emil'

from collections import namedtuple


Line = namedtuple('Line',
                  ['line_number',
                   'text'])


class LineSource:
    """
    Iterable over a sequence of Line:s.

    Line numbers start at 1.
    """

    def __iter__(self):
        raise NotImplementedError()


class _LineSourceForString(LineSource):
    def __init__(self, contents: str):
        self._lines = enumerate(contents.splitlines(),
                                start=1)

    def __iter__(self):
        for n, s in self._lines:
            yield Line(n, s)


def new_for_string(contents: str) -> LineSource:
    return _LineSourceForString(contents)


def new_for_file(file_name: str) -> LineSource:
    raise NotImplementedError()
