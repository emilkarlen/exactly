import io
import os
from abc import ABC
from typing import Optional, Sequence

from exactly_lib.util import ansi_terminal_color as ansi
from exactly_lib.util.ansi_terminal_color import ForegroundColor


class FilePrinter:
    """
    Printer that prints text a sequence of text lines on
    a file-like object.

    Optional support of ansi colors.
    """

    def __init__(self, file):
        """
        :param file: A file-like object.
        """
        self.file = file

    def write(self, s: str, flush: bool = False):
        self.file.write(s)
        if flush:
            self.file.flush()

    def write_line(self, line: str, indent: str = ''):
        self.file.write(indent + line)
        self.file.write(os.linesep)

    def write_colored_line(self, line: str, color: Optional[ForegroundColor]):
        self.file.write(line)
        self.file.write(os.linesep)

    def write_empty_line(self):
        self.file.write(os.linesep)

    def write_line_if_present(self, line: str):
        if line:
            self.write_line(line)

    def write_lines(self, lines: Sequence[str], indent: str = ''):
        for line in lines:
            self.write_line(indent + line)


class FilePrintable(ABC):
    """
    Something that is able to print itself on a FilePrinter.
    """

    def print_on(self, printer: FilePrinter):
        pass


class FilePrintableOfConstantString(FilePrintable):
    def __init__(self, s: str):
        self._s = s

    def print_on(self, printer: FilePrinter):
        printer.write(self._s)


class FilePrinterWithAnsiColor(FilePrinter):
    def write_colored_line(self, line: str, color: Optional[ForegroundColor]):
        s = ansi.ansi_escape(color, line) if color else line
        self.file.write(s)
        self.file.write(os.linesep)


def file_printer_with_color_if_terminal(file_object) -> FilePrinter:
    return (FilePrinterWithAnsiColor(file_object)
            if ansi.is_file_object_with_color(file_object)
            else FilePrinter(file_object))


def print_to_string(printable: FilePrintable) -> str:
    mem_file = io.StringIO()
    printable.print_on(FilePrinter(mem_file))
    ret_val = mem_file.getvalue()
    mem_file.close()
    return ret_val
