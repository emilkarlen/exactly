from typing import Sequence

from exactly_lib.common.report_rendering.parts import error_description, source_location
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.util.render import combinators as comb
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlocksRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class ErrorInfoRenderer(MajorBlocksRenderer):
    def __init__(self, error_info: ErrorInfo):
        self._error_info = error_info

    def render_sequence(self) -> Sequence[MajorBlock]:
        renderers = [
            source_location.location_blocks_renderer(
                self._error_info.source_location_path,
                self._error_info.maybe_section_name,
                None
            ),
            error_description.ErrorDescriptionRenderer(self._error_info.description),
        ]

        return comb.ConcatenationR(renderers).render_sequence()
