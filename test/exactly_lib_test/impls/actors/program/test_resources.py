import os
import pathlib
import tempfile
from abc import abstractmethod, ABC
from contextlib import contextmanager
from typing import List, ContextManager, Dict

from exactly_lib import program_info
from exactly_lib.impls.actors import common
from exactly_lib.impls.actors.program import actor as sut
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.actors.test_resources.action_to_check import Configuration, \
    TestCaseSourceSetup
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.util.test_resources import py_program


def shell_command_source_line_for(command: str) -> str:
    return common.SHELL_COMMAND_MARKER + ' ' + command


class ConfigurationWithPythonProgramBase(Configuration, ABC):
    def __init__(self):
        super().__init__(sut.actor())

    def program_that_copes_stdin_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(py_program.copy_stdin_to_stdout())

    def program_that_prints_to_stdout(self, string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(
            py_program.write_string_to_stdout(string_to_print))

    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(
            py_program.write_string_to_stderr(string_to_print))

    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str
                                                                    ) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    def program_that_prints_cwd_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(py_program.write_cwd_to_stdout())

    def program_that_exits_with_code(self, exit_code: int) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(py_program.exit_with_code(exit_code))

    def program_that_sleeps_at_least(self, number_of_seconds: int) -> ContextManager[TestCaseSourceSetup]:
        return self._instructions_for_executing_py_source(
            py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        )

    @abstractmethod
    @contextmanager
    def _instructions_for_executing_py_source(self, py_src: List[str]) -> ContextManager[TestCaseSourceSetup]:
        raise NotImplementedError('abstract method')


def valid_source_variants(program_line: str) -> List[NameAndValue[List[ActPhaseInstruction]]]:
    return [
        NameAndValue(
            'just program',
            [instr([program_line])],
        ),
        NameAndValue(
            'space and comments before program',
            [
                instr([
                    '   ',
                    LINE_COMMENT_MARKER + ' line comment',
                ]),
                instr([program_line]),
            ],
        ),
        NameAndValue(
            'space and comments after program',
            [
                instr([program_line]),
                instr([
                    '   ',
                    LINE_COMMENT_MARKER + ' line comment',
                ]),
            ],
        ),
        NameAndValue(
            'space and comments before and after program',
            [
                instr([
                    LINE_COMMENT_MARKER + ' line comment',
                ]),
                instr([program_line]),
                instr([
                    '   ',
                    LINE_COMMENT_MARKER + ' line comment',
                ]),
            ],
        ),
    ]


def invalid_source_variants(valid_program_line: str) -> List[NameAndValue[List[ActPhaseInstruction]]]:
    return [
        NameAndValue(
            'superfluous line after program',
            [instr([
                valid_program_line,
                'superfluous'
            ])],
        ),
        NameAndValue(
            'superfluous line after program and comment line',
            [instr([
                valid_program_line,
                LINE_COMMENT_MARKER + ' line comment',
                'superfluous'
            ])],
        ),
    ]


@contextmanager
def tmp_dir_in_path_with_files(files: DirContents) -> ContextManager[Dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME) as tmp_dir_name:
        environ = dict(os.environ)
        environ['PATH'] = os.pathsep.join((tmp_dir_name, environ['PATH']))

        files.write_to(pathlib.Path(tmp_dir_name))
        yield environ
