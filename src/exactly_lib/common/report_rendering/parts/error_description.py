from typing import Sequence, List

from exactly_lib.definitions import misc_texts
from exactly_lib.test_case import error_description
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.rendering.components import MajorBlocksRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock


class ErrorDescriptionRenderer(MajorBlocksRenderer):
    def __init__(self, description: error_description.ErrorDescription):
        self._description = description

    def render_sequence(self) -> Sequence[MajorBlock]:
        return _ErrorDescriptionDisplayer().visit(self._description)


class _ErrorDescriptionDisplayer(error_description.ErrorDescriptionVisitor[Sequence[MajorBlock]]):
    def _visit_message(self, ed: error_description.ErrorDescriptionOfMessage) -> Sequence[MajorBlock]:
        message_blocks = self._message_blocks(ed)
        return (
            [MajorBlock(message_blocks)]
            if message_blocks
            else []
        )

    def _visit_exception(self, ed: error_description.ErrorDescriptionOfException) -> Sequence[MajorBlock]:
        minor_blocks = self._message_blocks(ed)
        minor_blocks.append(
            struct.minor_block_from_lines([
                struct.StringLineObject('Exception:'),
                struct.PreFormattedStringLineObject(str(ed.exception), False),
            ])
        )

        return [MajorBlock(minor_blocks)]

    def _visit_external_process_error(self, ed: error_description.ErrorDescriptionOfExternalProcessError
                                      ) -> Sequence[MajorBlock]:
        minor_blocks = self._message_blocks(ed)
        lines = [struct.StringLineObject(misc_texts.EXIT_CODE.singular.capitalize() + ': ' +
                                         str(ed.external_process_error.exit_code))]

        if ed.external_process_error.stderr_output:
            lines.append(struct.PreFormattedStringLineObject(ed.external_process_error.stderr_output, False))

        minor_blocks.append(
            struct.minor_block_from_lines(lines)
        )

        return [MajorBlock(minor_blocks)]

    @staticmethod
    def _message_blocks(ed: error_description.ErrorDescription) -> List[MinorBlock]:
        return (
            []
            if ed.message is None
            else list(ed.message.render_sequence())
        )
