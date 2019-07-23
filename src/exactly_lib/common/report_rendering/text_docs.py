from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer, MinorTextRenderer
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import blocks, renderer_combinators as comb, \
    component_renderers as rend
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comp
from exactly_lib.util.simple_textstruct.structure import MinorBlock


def text_renderer_of_constant_minor_block(block: MinorBlock) -> TextRenderer:
    return comb.SingletonSequenceR(
        rend.MajorBlockR(
            comb.SingletonSequenceR(
                comb.ConstantR(block),
            ))
    )


def text_renderer_of_file_printable(fp: FilePrintable,
                                    is_line_ended: bool = False) -> TextRenderer:
    return blocks.MajorBlocksOfSingleLineObject(
        rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
    )


def minor_text_renderer_of_file_printable(fp: FilePrintable,
                                          is_line_ended: bool = False) -> MinorTextRenderer:
    return blocks.MinorBlocksOfSingleLineObject(
        rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
    )


def minor_text_renderer_of_file_printable__opt(fp: Optional[FilePrintable],
                                               is_line_ended: bool = False) -> Optional[MinorTextRenderer]:
    return (
        None
        if fp is None
        else blocks.MinorBlocksOfSingleLineObject(
            rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
        ))
