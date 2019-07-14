from abc import ABC
from typing import Optional

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.file_printer import FilePrinter


class PrintSettings:
    def __init__(self,
                 indent: str,
                 color: Optional[ForegroundColor],
                 font_style: Optional[FontStyle]):
        self.indent = indent
        self.color = color
        self.font_style = font_style

    def new_with_increased_indent(self, increase: str) -> 'PrintSettings':
        return PrintSettings(self.indent + increase,
                             self.color,
                             self.font_style)

    def new_with_color(self, color: ForegroundColor) -> 'PrintSettings':
        return PrintSettings(self.indent,
                             color,
                             self.font_style)

    def new_with_font_style(self, style: FontStyle) -> 'PrintSettings':
        return PrintSettings(self.indent,
                             self.color,
                             style)


class Printer:
    def __init__(self,
                 settings: PrintSettings,
                 file_printer: FilePrinter):
        self.settings = settings
        self.file_printer = file_printer

    @staticmethod
    def new(file_printer: FilePrinter) -> 'Printer':
        return Printer(PrintSettings('', None, None),
                       file_printer)

    def new_with_increased_indent(self, increase: str) -> 'Printer':
        """Gives a new printer with modified settings"""
        return Printer(self.settings.new_with_increased_indent(increase),
                       self.file_printer)

    def new_with_color(self, color: ForegroundColor) -> 'Printer':
        """Gives a new printer with modified settings"""
        return Printer(self.settings.new_with_color(color),
                       self.file_printer)

    def new_with_font_style(self, style: FontStyle) -> 'Printer':
        """Gives a new printer with modified settings"""
        return Printer(self.settings.new_with_font_style(style),
                       self.file_printer)

    def write_indented(self, s: str):
        self.file_printer.write(self.settings.indent)
        self.file_printer.write(s)

    def write_non_indented(self, s: str):
        self.file_printer.write(s)

    def new_line(self):
        self.file_printer.write_empty_line()

    def set_color(self):
        if self.settings.color is None:
            self.file_printer.unset_color()
        else:
            self.file_printer.set_color(self.settings.color)

    def set_font_style(self):
        if self.settings.font_style is None:
            self.file_printer.unset_font_style()
        else:
            self.file_printer.set_font_style(self.settings.font_style)


class Printable(ABC):
    def print_on(self, printer: Printer):
        pass
