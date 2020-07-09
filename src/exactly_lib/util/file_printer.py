import os
from typing import Optional, Sequence

from exactly_lib.util import ansi_terminal_color as ansi
from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle


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

    def flush(self):
        self.file.flush()

    def write(self, s: str, flush: bool = False):
        self.file.write(s)
        if flush:
            self.file.flush()

    def write_line(self, line: str, indent: str = ''):
        self.file.write(indent)
        self.file.write(line)
        self.file.write(os.linesep)

    def set_color(self, color: ForegroundColor):
        pass

    def unset_color(self):
        pass

    def set_font_style(self, style: FontStyle):
        pass

    def unset_font_style(self):
        pass

    def write_colored_line(self, line: str, color: Optional[ForegroundColor]):
        if color is not None:
            self.set_color(color)
        self.file.write(line)
        if color is not None:
            self.unset_color()
        self.file.write(os.linesep)

    def write_empty_line(self):
        self.file.write(os.linesep)

    def write_line_if_present(self, line: str):
        if line:
            self.write_line(line)

    def write_lines(self, lines: Sequence[str], indent: str = ''):
        for line in lines:
            self.write_line(indent)
            self.write_line(line)


class FilePrinterWithAnsiColor(FilePrinter):
    def set_color(self, color: ForegroundColor):
        self.file.write(ansi.set_color(color))

    def unset_color(self):
        self.file.write(ansi.unset_color())

    def set_font_style(self, style: FontStyle):
        self.file.write(ansi.set_font_style(style))

    def unset_font_style(self):
        self.file.write(ansi.unset_font_style())


def file_printer_with_color_if_terminal(file_object) -> FilePrinter:
    return (FilePrinterWithAnsiColor(file_object)
            if ansi.is_file_object_with_color(file_object)
            else FilePrinter(file_object))


def plain(file_object) -> FilePrinter:
    return FilePrinter(file_object)
