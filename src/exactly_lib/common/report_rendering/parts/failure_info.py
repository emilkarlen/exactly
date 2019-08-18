from typing import Sequence

from exactly_lib.common.report_rendering.parts import failure_details, source_location
from exactly_lib.execution.failure_info import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo, FailureInfo
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class FailureInfoRenderer(SequenceRenderer[MajorBlock]):
    def __init__(self, failure_info: FailureInfo):
        self._failure_info = failure_info

    def render(self) -> Sequence[MajorBlock]:
        everything = rend_comb.ConcatenationR([
            _GetFailureInfoLocationRenderer().visit(self._failure_info),
            failure_details.FailureDetailsRenderer(self._failure_info.failure_details)
        ])

        return everything.render()


class _GetFailureInfoLocationRenderer(FailureInfoVisitor[Renderer[Sequence[MajorBlock]]]):
    def _visit_phase_failure(self, failure_info: PhaseFailureInfo) -> Renderer[Sequence[MajorBlock]]:
        return source_location.location_blocks_renderer(
            None,
            failure_info.phase_step.phase.identifier,
            None
        )

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo) -> Renderer[Sequence[MajorBlock]]:
        return source_location.location_blocks_renderer(
            failure_info.source_location,
            failure_info.phase_step.phase.identifier,
            failure_info.element_description
        )