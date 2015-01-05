__author__ = 'emil'

import os
import pathlib
import unittest

from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import script_stmt_gen, py_cmd_gen


class Python3Language(script_stmt_gen.ScriptLanguage):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return ['python3', script_file_name]

    def base_name_from_stem(self, stem: str):
        return stem + '.py'

    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]


class PyCommandThatWritesToFileInTestRootDirBase(py_cmd_gen.PythonCommand):
    def __init__(self,
                 source_line: line_source.Line,
                 file_base_name: str):
        super().__init__(source_line)
        self.__file_base_name = file_base_name

    def apply(self, configuration: Configuration):
        file_path = configuration.test_root_dir / self.__file_base_name
        with open(str(file_path), 'w') as f:
            contents = os.linesep.join(self.file_lines(configuration)) + os.linesep
            f.write(contents)

    def file_lines(self, configuration) -> list:
        raise NotImplementedError()


def format_header_value_line(header: str, value: str) -> str:
    return '%-30s: %s' % (header, value)


def assert_is_file_with_contents(test: unittest.TestCase,
                                 file_path: pathlib.Path,
                                 expected_content: str):
    file_name = str(file_path)
    test.assertTrue(file_path.exists(),
                    'File should exist: ' + file_name)
    test.assertTrue(file_path.is_file(),
                    'Should be a regular file: ' + file_name)
    f = open(str(file_path))
    actual_contents = f.read()
    f.close()
    test.assertEqual(expected_content,
                     actual_contents,
                     'Contents of ' + file_name)