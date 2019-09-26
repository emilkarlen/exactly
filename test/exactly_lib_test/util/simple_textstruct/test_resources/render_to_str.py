import io
from typing import Sequence

from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct.file_printer_output import printables as ps
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import LayoutSettings, BlockSettings, \
    PrintablesFactory
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printable, Printer
from exactly_lib.util.simple_textstruct.structure import LineElement, MinorBlock, MajorBlock, ElementProperties


def lines_str(x: Sequence[str]) -> str:
    if len(x) == 0:
        return ''
    else:
        return '\n'.join(x) + '\n'


def blocks_str(blocks: Sequence[Sequence[str]]) -> str:
    return MINOR_BLOCKS_SEPARATOR.join([
        lines_str(block)
        for block in blocks
    ])


SINGLE_INDENT = ' '
MINOR_BLOCKS_SEPARATOR = '\n'
LAYOUT = LayoutSettings(
    major_block=BlockSettings(SINGLE_INDENT + SINGLE_INDENT + SINGLE_INDENT,
                              ps.SequencePrintable([ps.NEW_LINE_PRINTABLE,
                                                    ps.NEW_LINE_PRINTABLE])
                              ),
    minor_block=BlockSettings(SINGLE_INDENT + SINGLE_INDENT,
                              ps.NEW_LINE_PRINTABLE),
    line_element_indent=SINGLE_INDENT,
)


def print_line_element(line_element: LineElement) -> str:
    printable = PrintablesFactory(LAYOUT).line_element(line_element)
    return print_to_str(printable)


def print_line_elements(line_element: Sequence[LineElement]) -> str:
    block = MinorBlock(line_element, NO_INDENT_NO_COLOR_PROPERTIES)
    printable = PrintablesFactory(LAYOUT).minor_block(block)
    return print_to_str(printable)


def print_minor_blocks(blocks: Sequence[MinorBlock]) -> str:
    printable = PrintablesFactory(LAYOUT).minor_blocks(blocks)
    return print_to_str(printable)


def print_major_blocks(blocks: Sequence[MajorBlock]) -> str:
    printable = PrintablesFactory(LAYOUT).major_blocks(blocks)
    return print_to_str(printable)


def print_to_str(printable: Printable) -> str:
    output_file = io.StringIO()
    printer = Printer.new(FilePrinter(output_file))

    printable.print_on(printer)

    return output_file.getvalue()


NO_INDENT_NO_COLOR_PROPERTIES = ElementProperties(0, None)
