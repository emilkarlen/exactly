import os
from typing import Sequence, Any, Optional, Mapping


def lines_content(lines: Sequence[str]) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines) + '\n'


def lines_content_with_os_linesep(lines: list) -> str:
    return '' \
        if not lines \
        else os.linesep.join(lines) + os.linesep


def line_separated(lines: list) -> str:
    return '' \
        if not lines \
        else '\n'.join(lines)


def inside_parens(x) -> str:
    return '(' + str(x) + ')'


class StringFormatter:
    def __init__(self, format_map: Optional[Mapping[str, Any]] = None):
        self._format_map = {} if format_map is None else format_map

    def with_additional(self, format_map: Optional[Mapping[str, Any]]) -> 'StringFormatter':
        d = dict(self._format_map)
        d.update(format_map)
        return StringFormatter(d)

    def format(self, template: str, extra: Optional[Mapping[str, Any]] = None) -> str:
        """
        Formats the given string using the format map given in the constructor.
        """
        if extra is None:
            d = self._format_map
        else:
            d = dict(self._format_map)
            d.update(extra)
        return template.format_map(d)
