import io
from typing import Sequence

from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct.file_printer_output import printables as ps
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import LayoutSettings, BlockSettings, \
    PrintablesFactory
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printer, Printable
from exactly_lib.util.simple_textstruct.structure import MajorBlock

INDENT = '  '


def layout() -> LayoutSettings:
    return LayoutSettings(
        major_block=BlockSettings(INDENT,
                                  ps.SequencePrintable([ps.NEW_LINE_PRINTABLE,
                                                        ps.NEW_LINE_PRINTABLE])
                                  ),
        minor_block=BlockSettings(INDENT, ps.NEW_LINE_PRINTABLE),
        line_element_indent=INDENT,
    )


def major_blocks(text: Sequence[MajorBlock]) -> str:
    return _print_to_str(PrintablesFactory(layout()).major_blocks(text))


def _print_to_str(printable: Printable) -> str:
    output_file = io.StringIO()
    printer = Printer.new(FilePrinter(output_file))

    printable.print_on(printer)

    return output_file.getvalue()
