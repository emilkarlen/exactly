from typing import Sequence

from exactly_lib.common.report_rendering.parts import failure_details, source_location
from exactly_lib.definitions.entity import concepts
from exactly_lib.execution.failure_info import FailureInfoVisitor, ActPhaseFailureInfo, InstructionFailureInfo, \
    FailureInfo
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer, Renderer
from exactly_lib.util.simple_textstruct.rendering import line_objects, blocks, component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock
from exactly_lib.util.str_ import str_constructor


class FailureInfoRenderer(SequenceRenderer[MajorBlock]):
    def __init__(self, failure_info: FailureInfo):
        self._failure_info = failure_info

    def render_sequence(self) -> Sequence[MajorBlock]:
        everything = rend_comb.ConcatenationR([
            self._failure_info.accept(_GetFailureInfoLocationRenderer()),
            failure_details.FailureDetailsRenderer(self._failure_info.failure_details),
        ])

        return everything.render_sequence()


class _GetFailureInfoLocationRenderer(FailureInfoVisitor[SequenceRenderer[MajorBlock]]):
    def visit_act_phase_failure(self, failure_info: ActPhaseFailureInfo) -> SequenceRenderer[MajorBlock]:
        phase_source_and_actor = source_location.section_and_source(
            failure_info.phase_step.phase.identifier,
            rend_comb.PrependR(
                self._actor_info_block(failure_info.actor_name),
                source_location.source_str_renderer(failure_info.phase_source),
            )
        )

        return rend_comb.SingletonSequenceR(
            comp_rend.MajorBlockR(phase_source_and_actor)
        )

    def visit_instruction_failure(self, failure_info: InstructionFailureInfo) -> SequenceRenderer[MajorBlock]:
        return source_location.location_blocks_renderer(
            failure_info.source_location,
            failure_info.phase_step.phase.identifier,
            failure_info.element_description
        )

    @staticmethod
    def _actor_info_block(actor_name: str) -> Renderer[MinorBlock]:
        return blocks.MinorBlockOfSingleLineObject(
            line_objects.StringLineObject(
                str_constructor.FormatMap(
                    '{actor:/u} "{actor_name}"',
                    {
                        'actor': concepts.ACTOR_CONCEPT_INFO.name,
                        'actor_name': actor_name,
                    }
                )
            )
        )
