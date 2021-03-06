import pathlib
import subprocess
import tempfile
from typing import List

from exactly_lib import program_info
from exactly_lib.util.file_utils.misc_utils import resolved_path
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing, contents_of_file


class SubProcessResult(tuple):
    def __new__(cls,
                exitcode: int = 0,
                stdout: str = '',
                stderr: str = ''):
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


class ProcessExecutor:
    def execute(self, files: StdFiles) -> int:
        """
        :return: exit code
        """
        raise NotImplementedError()


class ProcessExecutorWoStdin:
    def execute(self, output: StdOutputFiles) -> int:
        """
        :return: exit code
        """
        raise NotImplementedError()


class ProcessExecutorForSubProcess(ProcessExecutor):
    def __init__(self,
                 cmd_and_args: List[str]):
        self.__cmd_and_args = cmd_and_args

    def execute(self, files: StdFiles) -> int:
        return subprocess.call(self.__cmd_and_args,
                               timeout=60,
                               stdin=files.stdin,
                               stdout=files.output.out,
                               stderr=files.output.err)


def capture_subprocess(cmd_and_args: List[str],
                       tmp_dir: pathlib.Path,
                       stdin_contents: str = '') -> SubProcessResult:
    return capture_process_executor_result(ProcessExecutorForSubProcess(cmd_and_args),
                                           tmp_dir,
                                           stdin_contents)


def capture_process_executor_result(executor: ProcessExecutor,
                                    tmp_dir: pathlib.Path,
                                    stdin_contents: str = '') -> SubProcessResult:
    stdout_path = tmp_dir / stdout_file_name
    stderr_path = tmp_dir / stderr_file_name
    stdin_path = tmp_dir / stdin_file_name
    with open(str(stdin_path), 'w') as f_stdin:
        f_stdin.write(stdin_contents)
    with open(str(stdin_path)) as f_stdin:
        with open(str(stdout_path), 'w') as f_stdout:
            with open(str(stderr_path), 'w') as f_stderr:
                exitcode = executor.execute(StdFiles(f_stdin,
                                                     StdOutputFiles(f_stdout,
                                                                    f_stderr)))
    return SubProcessResult(exitcode,
                            contents_of_file(stdout_path),
                            contents_of_file(stderr_path))


def capture_process_executor_result__wo_stdin(executor: ProcessExecutorWoStdin,
                                              tmp_dir: pathlib.Path) -> SubProcessResult:
    stdout_path = tmp_dir / stdout_file_name
    stderr_path = tmp_dir / stderr_file_name
    with open(str(stdout_path), 'w') as f_stdout:
        with open(str(stderr_path), 'w') as f_stderr:
            exitcode = executor.execute(StdOutputFiles(f_stdout, f_stderr))
    return SubProcessResult(exitcode,
                            contents_of_file(stdout_path),
                            contents_of_file(stderr_path))


def run_subprocess(cmd_and_args: List[str],
                   stdin_contents: str = '') -> SubProcessResult:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir:
        return capture_subprocess(cmd_and_args,
                                  resolved_path(tmp_dir),
                                  stdin_contents=stdin_contents)


class SubProcessResultInfo(tuple):
    def __new__(cls,
                file_argument: pathlib.Path,
                sub_process_result: SubProcessResult):
        return tuple.__new__(cls, (file_argument, sub_process_result))

    @property
    def file_argument(self) -> pathlib.Path:
        return self[0]

    @property
    def sub_process_result(self) -> SubProcessResult:
        return self[1]


def run_subprocess_with_file_arg__full(cmd_and_args_except_file_arg: List[str],
                                       file_contents: str) -> SubProcessResultInfo:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir_name:
        tmp_dir_path = pathlib.Path(tmp_dir_name).resolve()
        with tmp_file_containing(file_contents, directory=str(tmp_dir_path)) as file_path:
            cmd_and_args = cmd_and_args_except_file_arg + [str(file_path)]
            sub_process_result = capture_subprocess(cmd_and_args,
                                                    tmp_dir_path)
            return SubProcessResultInfo(file_path,
                                        sub_process_result)
