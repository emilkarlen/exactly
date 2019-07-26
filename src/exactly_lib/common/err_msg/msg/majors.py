from typing import Any

from exactly_lib.common.err_msg.msg import minors
from exactly_lib.common.report_rendering.text_doc import TextRenderer, MinorTextRenderer
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import blocks, renderer_combinators as comb, \
    component_renderers as rend, renderer_combinators as rend_comp
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


def single_file_printable(fp: FilePrintable,
                          is_line_ended: bool = False) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
    )
