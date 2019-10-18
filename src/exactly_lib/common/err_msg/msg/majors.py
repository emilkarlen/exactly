from typing import Any

from exactly_lib.common.err_msg.msg import minors
from exactly_lib.common.report_rendering.text_doc import TextRenderer, MinorTextRenderer
from exactly_lib.util.render import combinators as comb
from exactly_lib.util.simple_textstruct.rendering import component_renderers as rend
from exactly_lib.util.simple_textstruct.structure import MinorBlock


def of_minor(text: MinorTextRenderer) -> TextRenderer:
    return comb.SingletonSequenceR(
        rend.MajorBlockR(text)
    )


def of_pre_formatted_message(message_str: Any) -> TextRenderer:
    return comb.SingletonSequenceR(
        rend.MajorBlockR(minors.single_pre_formatted(message_str))
    )


def single_constant_minor(block: MinorBlock) -> TextRenderer:
    return comb.SingletonSequenceR(
        rend.MajorBlockR(
            comb.SingletonSequenceR(
                comb.ConstantR(block),
            )
        )
    )
