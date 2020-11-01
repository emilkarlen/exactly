from typing import Optional, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class ErrorMessageWithFixTip(SequenceRenderer[MajorBlock]):
    def __init__(self,
                 message: TextRenderer,
                 how_to_fix: Optional[TextRenderer] = None,
                 ):
        self._message = message
        self._how_to_fix = how_to_fix

    @property
    def message(self) -> TextRenderer:
        return self._message

    @property
    def how_to_fix(self) -> Optional[TextRenderer]:
        return self._how_to_fix

    def render_sequence(self) -> Sequence[MajorBlock]:
        ret_val = list(self.message.render_sequence())
        if self.how_to_fix is not None:
            ret_val += self.how_to_fix.render_sequence()

        return ret_val

    def __str__(self) -> str:
        from exactly_lib.util.simple_textstruct.file_printer_output import to_string
        return '%s{message=%s, how_to_fix=%s}' % (
            type(self),
            to_string.major_blocks(self.message.render_sequence()),
            (''
             if self.how_to_fix is None
             else to_string.major_blocks(self.how_to_fix.render_sequence())
             )
        )
