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


class StdFiles:
    def __init__(self,
                 stdin_file=sys.stdin,
                 output_files: StdOutputFiles=StdOutputFiles()):
        self._stdin_file = stdin_file
        self._output_files = output_files

    @property
    def stdin(self):
        return self._stdin_file

    @property
    def output(self) -> StdOutputFiles:
        return self._output_files
