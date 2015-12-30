import io

from shellcheck_lib.general.std import StdOutputFiles


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
