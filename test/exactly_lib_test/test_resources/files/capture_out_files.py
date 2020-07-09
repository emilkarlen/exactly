import tempfile
from typing import TypeVar, Callable, Tuple

from exactly_lib.util.file_utils.std import StdOutputFiles, StdOutputFilesContents

ResultType = TypeVar('ResultType')


def capture_stdout_err(action: Callable[[StdOutputFiles], ResultType]) -> Tuple[StdOutputFilesContents, ResultType]:
    with tempfile.TemporaryFile(mode='r+t') as stdout_file:
        with tempfile.TemporaryFile(mode='r+t') as stderr_file:
            std_files = StdOutputFiles(stdout_file, stderr_file)
            result = action(std_files)

            stdout_file_contents = _contents_of(stdout_file)
            stderr_file_contents = _contents_of(stderr_file)

            return StdOutputFilesContents(stdout_file_contents, stderr_file_contents), result


def _contents_of(f) -> str:
    f.seek(0)
    return f.read()
