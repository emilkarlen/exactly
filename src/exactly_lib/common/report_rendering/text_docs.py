from typing import Any

from exactly_lib.common.report_rendering import print
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrinter, FilePrintable
from exactly_lib.util.simple_textstruct.file_printer_output import printer as printer_
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import PrintablesFactory
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects


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


class _TextRendererAsFilePrintable(FilePrintable):
    def __init__(self, blocks: TextRenderer):
        self._blocks = blocks

    def print_on(self, printer: FilePrinter):
        printable = PrintablesFactory(print.layout()).major_blocks(self._blocks.render())
        printable.print_on(printer_.Printer.new(printer))
