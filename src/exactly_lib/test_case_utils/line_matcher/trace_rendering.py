from typing import Sequence

from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib.util.str_ import str_constructor


class LineMatcherLineRenderer(DetailsRenderer):
    def __init__(self, line: LineMatcherLine):
        self._line = line

    def render(self) -> Sequence[Detail]:
        line = self._line
        return [
            tree.StringDetail(
                str_constructor.FormatPositional(
                    'Line {}. {}',
                    line[0],
                    repr(line[1]),
                )
            )
        ]
