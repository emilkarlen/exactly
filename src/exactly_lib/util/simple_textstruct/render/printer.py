from abc import ABC
from typing import Optional

from exactly_lib.util.ansi_terminal_color import ForegroundColor
from exactly_lib.util.file_printer import FilePrinter


class PrintSettings:
    def __init__(self,
                 indent: str,
                 color: Optional[ForegroundColor]):
        self.indent = indent
        self.color = color

    def new_with_increased_indent(self, increase: str) -> 'PrintSettings':
        return PrintSettings(self.indent + increase,
                             self.color)

    def new_with_color(self, color: ForegroundColor) -> 'PrintSettings':
        return PrintSettings(self.indent,
                             color)


class Printer:
    def __init__(self,
                 settings: PrintSettings,
                 file_printer: FilePrinter):
        self.settings = settings
        self.file_printer = file_printer

    def new_with_increased_indent(self, increase: str) -> 'Printer':
        """Gives a new printer with modified settings"""
        return Printer(self.settings.new_with_increased_indent(increase),
                       self.file_printer)

    def new_with_color(self, color: ForegroundColor) -> 'Printer':
        """Gives a new printer with modified settings"""
        return Printer(self.settings.new_with_color(color),
                       self.file_printer)

    def write_indented(self, s: str):
        self.file_printer.write(self.settings.indent)
        self.file_printer.write(s)

    def new_line(self):
        self.file_printer.write_empty_line()

    def set_color(self):
        if self.settings.color is None:
            self.file_printer.unset_color()
        else:
            self.file_printer.set_color(self.settings.color)


class Printable(ABC):
    def print_on(self, printer: Printer):
        pass
