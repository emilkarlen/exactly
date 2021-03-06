import os
import pathlib
import unittest


def format_header_value_line(header: str, value: str) -> str:
    return '%-30s: %s' % (header, value)


def un_lines(lines: list) -> str:
    return os.linesep.join(lines) + os.linesep


def assert_is_file_with_contents(test: unittest.TestCase,
                                 file_path: pathlib.Path,
                                 expected_content: str,
                                 msg=None):
    file_name = str(file_path)
    test.assertTrue(file_path.exists(),
                    'File should exist: ' + file_name)
    test.assertTrue(file_path.is_file(),
                    'Should be a regular file: ' + file_name)
    f = open(str(file_path))
    actual_contents = f.read()
    f.close()
    if msg is None:
        msg = 'Contents of:' + file_name
    test.assertEqual(expected_content,
                     actual_contents,
                     msg)
