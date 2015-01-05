import os

__author__ = 'emil'

import pathlib
import unittest

from shelltest.exec_abs_syn import script_stmt_gen


class Python3Language(script_stmt_gen.ScriptLanguage):
    def command_and_args_for_executing_script_file(self, script_file_name: str) -> list:
        return ['python3', script_file_name]

    def base_name_from_stem(self, stem: str):
        return stem + '.py'

    def comment_line(self, comment: str) -> list:
        return ['# ' + comment]

    def raw_script_statement(self, statement: str) -> list:
        return [statement]


def format_header_value_line(header: str, value: str) -> str:
    return '%-30s: %s' % (header, value)


def un_lines(lines: list) -> str:
    return os.linesep.join(lines) + os.linesep


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
                     'Contents of:' + file_name)
