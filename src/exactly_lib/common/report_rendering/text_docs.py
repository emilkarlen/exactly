from typing import Any, Sequence

from exactly_lib.common.err_msg.definitions import Blocks, Block
from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrinter, FilePrintable
from exactly_lib.util.simple_textstruct.file_printer_output import printer as printer_
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import PrintablesFactory
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering import \
    renderer_combinators as rend_comb, \
    component_renderers as comp_rend
from exactly_lib.util.simple_textstruct.rendering.components import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock, LineElement, PreFormattedStringLineObject, \
    MajorBlock


def single_pre_formatted_line_object(x: Any,
                                     is_line_ended: bool = False) -> TextRenderer:
    """
    :param is_line_ended: Tells if the string str(x) ends with a new-line character.
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.PreFormattedString(x, is_line_ended)
    )


def single_line(x: Any) -> TextRenderer:
    """
    :param x: __str__ gives the string
    """
    return blocks.MajorBlocksOfSingleLineObject(
        line_objects.StringLineObject(x)
    )


def single_pre_formatted_line_object__from_fp(fp: FilePrintable) -> TextRenderer:
    return single_pre_formatted_line_object(file_printables.print_to_string(fp))


def as_file_printable(x: TextRenderer) -> FilePrintable:
    return _TextRendererAsFilePrintable(x)


def minor_blocks_of_string_blocks(contents: Blocks) -> Renderer[Sequence[MinorBlock]]:
    return _OfBlocks(contents)


def major_block_of_string_blocks(contents: Blocks) -> Renderer[Sequence[MajorBlock]]:
    return comp_rend.MajorBlockR(minor_blocks_of_string_blocks(contents))


def major_blocks_of_string_blocks(contents: Blocks) -> Renderer[Sequence[MajorBlock]]:
    return rend_comb.SingletonSequenceR(
        major_block_of_string_blocks(contents)
    )


class _TextRendererAsFilePrintable(FilePrintable):
    def __init__(self, blocks: TextRenderer):
        self._blocks = blocks

    def print_on(self, printer: FilePrinter):
        printable = PrintablesFactory(print.layout()).major_blocks(self._blocks.render())
        printable.print_on(printer_.Printer.new(printer))


class _OfBlocks(SequenceRenderer[MinorBlock]):
    def __init__(self, contents: Blocks):
        self._contents = contents

    def render(self) -> Sequence[MinorBlock]:
        return [
            _mk_minor_block(lines)
            for lines in self._contents
        ]


def _mk_minor_block(lines: Block) -> MinorBlock:
    return MinorBlock([
        LineElement(
            PreFormattedStringLineObject(line, False)
        )
        for line in lines
    ]
    )
