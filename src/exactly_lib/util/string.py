import os
from typing import Sequence, Any, Optional, Mapping

from exactly_lib.util.name_and_value import NameAndValue


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

    @staticmethod
    def of_name_and_values(elements: Sequence[NameAndValue[Any]]) -> 'StringFormatter':
        return StringFormatter({
            element.name: element.value
            for element in elements
        })

    def with_additional(self,
                        format_map: Optional[Mapping[str, Any]],
                        **keyword_mappings) -> 'StringFormatter':
        d = dict(self._format_map)
        d.update(format_map)
        return StringFormatter(self._get_format_map(format_map, **keyword_mappings))

    def format(self,
               template: str,
               extra: Optional[Mapping[str, Any]] = None,
               **keyword_mappings) -> str:
        """
        Formats the given string using the format map given in the constructor.
        """
        return template.format_map(self._get_format_map(extra, **keyword_mappings))

    def _get_format_map(self,
                        extra: Optional[Mapping[str, Any]] = None,
                        **keyword_mappings) -> Mapping[str, Any]:
        if extra is None and not keyword_mappings:
            return self._format_map

        ret_val = dict(self._format_map)
        if extra is not None:
            ret_val.update(extra)
        if keyword_mappings:
            ret_val.update(keyword_mappings)

        return ret_val
