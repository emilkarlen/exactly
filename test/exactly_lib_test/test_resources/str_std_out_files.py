import io

from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.test_resources.file_utils import NullFile


def null_output_files() -> StdOutputFiles:
    return StdOutputFiles(NullFile(),
                          NullFile())


class StringStdOutFiles:
    def __init__(self):
        self._stdout_file = io.StringIO()
        self._stderr_file = io.StringIO()
        self._stdout_files = StdOutputFiles(self._stdout_file,
                                            self._stderr_file)
        self._stdout_contents = ''
        self._stderr_contents = ''

    def finish(self):
        self._stdout_contents = self._stdout_file.getvalue()
        self._stdout_file.close()
        self._stderr_contents = self._stderr_file.getvalue()
        self._stderr_file.close()

    @property
    def stdout_files(self) -> StdOutputFiles:
        return self._stdout_files

    @property
    def stdout_contents(self) -> str:
        return self._stdout_contents

    @property
    def stderr_contents(self) -> str:
        return self._stderr_contents
