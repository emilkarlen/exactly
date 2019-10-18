from typing import Sequence, List

from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class FailureDetailsRenderer(SequenceRenderer[MajorBlock]):
    def __init__(self, failure_details: FailureDetails):
        self._failure_details = failure_details

    def render_sequence(self) -> Sequence[MajorBlock]:
        blocks = self._exception_blocks()
        blocks += self._message_blocks()

        return blocks

    def _message_blocks(self) -> List[MajorBlock]:
        message_renderer = self._failure_details.failure_message
        return (
            []
            if message_renderer is None
            else message_renderer.render_sequence()
        )

    def _exception_blocks(self) -> List[MajorBlock]:
        if not self._failure_details.has_exception:
            return []

        ex = self._failure_details.exception

        return [
            MajorBlock([
                struct.minor_block_from_lines([
                    struct.StringLineObject('Exception'),
                ]),
                struct.minor_block_from_lines([
                    struct.PreFormattedStringLineObject(str(ex), False),
                ]),
            ])
        ]
