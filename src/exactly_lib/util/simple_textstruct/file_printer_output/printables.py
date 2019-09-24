from typing import Sequence

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printable, Printer


class SequencePrintable(Printable):
    def __init__(self, printables: Sequence[Printable]):
        self._printables = printables

    def print_on(self, printer: Printer):
        for printable in self._printables:
            printable.print_on(printer)


class InterspersedSequencePrintable(Printable):
    def __init__(self,
                 interspersed_printable: Printable,
                 printables: Sequence[Printable]):
        self._interspersed_printable = interspersed_printable
        self._printables = printables

    def print_on(self, printer: Printer):
        if len(self._printables) >= 1:
            self._printables[0].print_on(printer)
        for printable in self._printables[1:]:
            self._interspersed_printable.print_on(printer)
            printable.print_on(printer)


class IncreasedIndentPrintable(Printable):
    def __init__(self,
                 increase: str,
                 printable: Printable):
        self._increase = increase
        self._printable = printable

    def print_on(self, printer: Printer):
        self._printable.print_on(printer.new_with_increased_indent(self._increase))


class ColoredPrintable(Printable):
    def __init__(self,
                 color: ForegroundColor,
                 printable: Printable):
        self._color = color
        self._printable = printable

    def print_on(self, printer: Printer):
        colored_printer = printer.new_with_color(self._color)
        colored_printer.set_color()
        self._printable.print_on(colored_printer)
        printer.set_color()


class FontStyledPrintable(Printable):
    def __init__(self,
                 style: FontStyle,
                 printable: Printable):
        self._style = style
        self._printable = printable

    def print_on(self, printer: Printer):
        styled_printer = printer.new_with_font_style(self._style)
        styled_printer.set_font_style()
        self._printable.print_on(styled_printer)
        printer.set_font_style()


class NewLinePrintable(Printable):
    def print_on(self, printer: Printer):
        printer.new_line()


NEW_LINE_PRINTABLE = NewLinePrintable()
