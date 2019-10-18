from typing import Sequence

from exactly_lib.common.report_rendering.parts import failure_details, source_location
from exactly_lib.execution.failure_info import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo, FailureInfo
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class FailureInfoRenderer(SequenceRenderer[MajorBlock]):
    def __init__(self, failure_info: FailureInfo):
        self._failure_info = failure_info

    def render_sequence(self) -> Sequence[MajorBlock]:
        everything = rend_comb.ConcatenationR([
            _GetFailureInfoLocationRenderer().visit(self._failure_info),
            failure_details.FailureDetailsRenderer(self._failure_info.failure_details)
        ])

        return everything.render_sequence()


class _GetFailureInfoLocationRenderer(FailureInfoVisitor[SequenceRenderer[MajorBlock]]):
    def _visit_phase_failure(self, failure_info: PhaseFailureInfo) -> SequenceRenderer[MajorBlock]:
        return source_location.location_blocks_renderer(
            None,
            failure_info.phase_step.phase.identifier,
            None
        )

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo) -> SequenceRenderer[MajorBlock]:
        return source_location.location_blocks_renderer(
            failure_info.source_location,
            failure_info.phase_step.phase.identifier,
            failure_info.element_description
        )
