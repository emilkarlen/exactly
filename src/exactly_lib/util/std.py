import os
import subprocess
import sys


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

    def write_empty_line(self):
        self.file.write(os.linesep)

    def write_line_if_present(self, line: str):
        if line:
            self.write_line(line)

    def write_lines(self, lines: iter):
        for line in lines:
            self.write_line(line)
