from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct.render import printables as ps
from exactly_lib.util.simple_textstruct.render.print_on_file_printer import LayoutSettings, BlockSettings, \
    PrintablesFactory
from exactly_lib.util.simple_textstruct.render.printer import Printer
from exactly_lib.util.simple_textstruct.structure import LineElement


def layout() -> LayoutSettings:
    return LayoutSettings(
        major_block=BlockSettings('  ',
                                  ps.SequencePrintable([ps.NEW_LINE_PRINTABLE,
                                                        ps.NEW_LINE_PRINTABLE])
                                  ),
        minor_block=BlockSettings('  ', ps.NEW_LINE_PRINTABLE),
        line_element_indent='  ',
    )


def print_line_element(line_element: LineElement,
                       file_printer: FilePrinter):
    printable = PrintablesFactory(layout()).line_element(line_element)
    printable.print_on(Printer.new(file_printer))
