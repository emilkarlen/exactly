import os
import subprocess
import sys
from typing import Optional

from exactly_lib.util import ansi_terminal_color as ansi
from exactly_lib.util.ansi_terminal_color import ForegroundColor


class StdOutputFiles:
    def __init__(self,
                 stdout_file=sys.stdout,
                 stderr_file=sys.stderr):
        self._stdout_file = stdout_file
        self._stderr_file = stderr_file

    @property
    def out(self):
        return self._stdout_file

    @property
    def err(self):
        return self._stderr_file


class StdOutputFilesContents:
    def __init__(self,
                 stdout_file: str,
                 stderr_file: str):
        self._stdout_file = stdout_file
        self._stderr_file = stderr_file

    @property
    def out(self) -> str:
        return self._stdout_file

    @property
    def err(self) -> str:
        return self._stderr_file


def new_std_output_files_dev_null() -> StdOutputFiles:
    return StdOutputFiles(subprocess.DEVNULL,
                          subprocess.DEVNULL)


class StdFiles:
    def __init__(self,
                 stdin_file=sys.stdin,
                 output_files: StdOutputFiles = StdOutputFiles()):
        self._stdin_file = stdin_file
        self._output_files = output_files

    @property
    def stdin(self):
        return self._stdin_file

    @property
    def output(self) -> StdOutputFiles:
        return self._output_files


def std_files_dev_null() -> StdFiles:
    return StdFiles(subprocess.DEVNULL,
                    new_std_output_files_dev_null())


class FilePrinter:
    def __init__(self, file):
        self.file = file

    def write(self, s: str, flush: bool = False):
        self.file.write(s)
        if flush:
            self.file.flush()

    def write_line(self, line: str):
        self.file.write(line)
        self.file.write(os.linesep)

    def write_colored_line(self, line: str, color: Optional[ForegroundColor]):
        self.file.write(line)
        self.file.write(os.linesep)

    def write_empty_line(self):
        self.file.write(os.linesep)

    def write_line_if_present(self, line: str):
        if line:
            self.write_line(line)

    def write_lines(self, lines: iter):
        for line in lines:
            self.write_line(line)


class FilePrinterWithAnsiColor(FilePrinter):
    def write_colored_line(self, line: str, color: Optional[ForegroundColor]):
        s = ansi.ansi_escape(color, line) if color else line
        self.file.write(s)
        self.file.write(os.linesep)


def file_printer_with_color_if_terminal(file_object) -> FilePrinter:
    return (FilePrinterWithAnsiColor(file_object)
            if ansi.is_file_object_with_color(file_object)
            else FilePrinter(file_object))
