from typing import Sequence

from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace.trace import Detail
from exactly_lib.type_system.trace.trace_renderer import DetailsRenderer
from exactly_lib.util import strings


class LineMatcherLineRenderer(DetailsRenderer):
    def __init__(self, line: LineMatcherLine):
        self._line = line

    def render(self) -> Sequence[Detail]:
        line = self._line
        return [
            trace.StringDetail(
                strings.FormatPositional('Line {}: {}',
                                         line[0],
                                         repr(line[1]))
            )
        ]
