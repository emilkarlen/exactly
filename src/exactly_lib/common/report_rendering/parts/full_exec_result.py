from typing import Sequence

from exactly_lib.common.report_rendering.parts import failure_info
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlocksRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class FullExeResultRenderer(MajorBlocksRenderer):
    _EMPTY = rend_comb.ConstantSequenceR([])

    def __init__(self, full_result: FullExeResult):
        self._result = full_result

    def render_sequence(self) -> Sequence[MajorBlock]:
        return self._renderer().render_sequence()

    def _renderer(self) -> SequenceRenderer[MajorBlock]:
        return (
            failure_info.FailureInfoRenderer(self._result.failure_info)
            if self._result.is_failure
            else self._EMPTY
        )
