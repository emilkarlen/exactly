from contextlib import contextmanager
import os
import pathlib
import tempfile
import subprocess


def lines_content(lines: list) -> str:
    return os.linesep.join(lines) + os.linesep


@contextmanager
def tmp_file_containing(contents: str,
                        suffix: str='',
                        dir=None) -> pathlib.Path:
    """
    Returns a context manager (used by with tmp_file(...) as file_path) ...
    The context manager takes care of deleting the file.

    :param contents: The contents of the returned file.
    :param suffix: A possible suffix of the file name (a dot does not automatically separate stem, suffix).
    :return: File path of a closed text file with the given contents.
    """
    path = None
    try:
        fd, absolute_file_path = tempfile.mkstemp(prefix='shelltest-test-',
                                                  suffix=suffix,
                                                  dir=dir,
                                                  text=True)
        fo = os.fdopen(fd, "w+")
        fo.write(contents)
        fo.close()
        path = pathlib.Path(absolute_file_path)
        yield path
    finally:
        if path:
            path.unlink()


def tmp_file_containing_lines(content_lines: list,
                              suffix: str='') -> pathlib.Path:
    """
    Short cut to tmp_file_containing combined with giving the contents as a string of lines.
    """
    return tmp_file_containing(lines_content(content_lines),
                               suffix=suffix)


class SubProcessResult(tuple):
    def __new__(cls,
                exitcode: int,
                stdout: str,
                stderr: str):
        return tuple.__new__(cls, (exitcode, stdout, stderr))

    @property
    def exitcode(self) -> int:
        return self[0]

    @property
    def stdout(self) -> str:
        return self[1]

    @property
    def stderr(self) -> str:
        return self[2]


stdout_file_name = 'stdout.txt'
stderr_file_name = 'stderr.txt'
stdin_file_name = 'stdin.txt'


def capture_subprocess(cmd_and_args: list,
                       tmp_dir: pathlib.Path,
                       cwd: str=None,
                       stdin_contents: str='') -> SubProcessResult:
    stdout_path = tmp_dir / stdout_file_name
    stderr_path = tmp_dir / stderr_file_name
    stdin_path = tmp_dir / stdin_file_name
    with open(str(stdin_path), 'w') as f_stdin:
        f_stdin.write(stdin_contents)
    with open(str(stdin_path)) as f_stdin:
        with open(str(stdout_path), 'w') as f_stdout:
            with open(str(stderr_path), 'w') as f_stderr:
                exitcode = subprocess.call(cmd_and_args,
                                           cwd=cwd,
                                           stdin=f_stdin,
                                           stdout=f_stdout,
                                           stderr=f_stderr)
    return SubProcessResult(exitcode,
                            _contents_of_file(stdout_path),
                            _contents_of_file(stderr_path))


def _contents_of_file(path: pathlib.Path) -> str:
    with open(str(path)) as f:
        return f.read()


def run_subprocess(cmd_and_args: list,
                   stdin_contents: str='') -> SubProcessResult:
    with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_dir:
        return capture_subprocess(cmd_and_args,
                                  pathlib.Path(tmp_dir),
                                  stdin_contents=stdin_contents)


def run_subprocess_with_file_arg(cmd_and_args_except_file_arg: list,
                                 file_contents: str,
                                 stdin_contents: str='') -> SubProcessResult:
    with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_dir_name:
        with tmp_file_containing(file_contents, dir=tmp_dir_name) as file_path:
            cmd_and_args = cmd_and_args_except_file_arg + [str(file_path)]
            return capture_subprocess(cmd_and_args,
                                      pathlib.Path(tmp_dir_name),
                                      stdin_contents=stdin_contents)
