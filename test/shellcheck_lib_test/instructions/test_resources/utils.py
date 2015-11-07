from contextlib import contextmanager
import os
import pathlib
import tempfile
from time import strftime, localtime

from shellcheck_lib.document import parse
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.execution import execution_directory_structure as eds_module
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSequenceBuilder
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib_test.util.file_utils import write_file


class ActResult:
    def __init__(self,
                 exitcode: int=0,
                 stdout_contents: str='',
                 stderr_contents: str=''):
        self._exitcode = exitcode
        self._stdout_contents = stdout_contents
        self._stderr_contents = stderr_contents

    @property
    def exitcode(self) -> int:
        return self._exitcode

    @property
    def stdout_contents(self) -> str:
        return self._stdout_contents

    @property
    def stderr_contents(self) -> str:
        return self._stderr_contents


@contextmanager
def act_phase_result(exitcode: int=0,
                     stdout_contents: str='',
                     stderr_contents: str='') -> i.GlobalEnvironmentForPostEdsPhase:
    cwd_before = os.getcwd()
    home_dir_path = pathlib.Path(cwd_before)
    with tempfile.TemporaryDirectory(prefix='shellcheck-test-') as eds_root_dir:
        eds = execution_directory_structure.construct_at(eds_root_dir)
        write_file(eds.result.exitcode_file, str(exitcode))
        write_file(eds.result.stdout_file, stdout_contents)
        write_file(eds.result.stderr_file, stderr_contents)
        try:
            os.chdir(str(eds.act_dir))
            yield i.GlobalEnvironmentForPostEdsPhase(home_dir_path,
                                                     eds)
        finally:
            os.chdir(cwd_before)


class HomeAndEds:
    def __init__(self,
                 home_path: pathlib.Path,
                 eds: eds_module.ExecutionDirectoryStructure):
        self._home_path = home_path
        self._eds = eds

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self._home_path

    @property
    def eds(self) -> eds_module.ExecutionDirectoryStructure:
        return self._eds

    def write_act_result(self,
                         result: ActResult):
        write_file(self.eds.result.exitcode_file, str(result.exitcode))
        write_file(self.eds.result.stdout_file, result.stdout_contents)
        write_file(self.eds.result.stderr_file, result.stderr_contents)


@contextmanager
def home_and_eds_and_test_as_curr_dir() -> HomeAndEds:
    cwd_before = os.getcwd()
    prefix = strftime("shellcheck-test-%Y-%m-%d-%H-%M-%S", localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir:
        home_dir_path = pathlib.Path(home_dir)
        with execution_directory_structure(prefix=prefix + "-eds-") as eds:
            try:
                os.chdir(str(eds.act_dir))
                yield HomeAndEds(home_dir_path,
                                 eds)
            finally:
                os.chdir(cwd_before)


@contextmanager
def execution_directory_structure(prefix: str='shellcheck-test-eds-') -> eds_module.ExecutionDirectoryStructure:
    with tempfile.TemporaryDirectory(prefix=prefix) as eds_root_dir:
        eds = eds_module.construct_at(eds_root_dir)
        yield eds


def new_source(instruction_name: str, arguments: str) -> SingleInstructionParserSource:
    first_line = instruction_name + ' ' + arguments
    return SingleInstructionParserSource(
        new_line_sequence(first_line),
        arguments)


def new_line_sequence(first_line: str) -> LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines([])),
        1,
        first_line)
