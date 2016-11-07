"""
This module should probably be replaced by corresponding ValueAssertion in file_assertions
"""
import pathlib
import unittest

from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.assertions import assert_utils


class FileChecker:
    def __init__(self,
                 put: unittest.TestCase,
                 message_header: str = None):
        self.put = put
        self.message_header = message_header

    def assert_is_existing_empty_dir(self, p: pathlib.Path):
        self.assert_exists_dir_with_given_number_of_files_in_it(p, 0)

    def assert_exists_dir_with_given_number_of_files_in_it(self,
                                                           p: pathlib.Path,
                                                           expected_number_of_files: int):
        self.assert_exists_dir(p)
        directory_contents = list(p.iterdir())
        self.put.assertEquals(
            expected_number_of_files,
            len(directory_contents),
            self._msg('The directory "%s" should contain exactly %s files. Found %s' % (str(p),
                                                                                        expected_number_of_files,
                                                                                        str(directory_contents))))

    def assert_exists_dir(self, p: pathlib.Path):
        self.put.assertTrue(p.exists(), self._msg('"%s" should exist (as a directory)' % p.name))
        self.put.assertTrue(p.is_dir(), self._msg('"%s" should be a directory' % p.name))

    def assert_exists_plain_file(self, p: pathlib.Path):
        self.put.assertTrue(p.exists(), self._msg('"%s" should exist (as a plain file)' % p.name))
        self.put.assertTrue(p.is_file(), self._msg('"%s" should be a plain file' % p.name))

    def assert_file_contents(self,
                             p: pathlib.Path,
                             expected_contents: str):
        with p.open() as f:
            actual_contents = f.read()
            self.put.assertEqual(expected_contents,
                                 actual_contents,
                                 'The file {} should contain exactly "{}"'.format(str(p),
                                                                                  expected_contents))

    def assert_is_plain_file_with_contents(self,
                                           p: pathlib.Path,
                                           expected_contents: str):
        self.assert_exists_plain_file(p)
        self.assert_file_contents(p, expected_contents)

    def assert_dir_contents_matches_exactly(self,
                                            dir_path: pathlib.Path,
                                            expected: file_structure.DirContents):
        return self.assert_dir_matches_exactly(dir_path, expected.file_system_element_contents)

    def assert_dir_matches_exactly(self,
                                   dir_path: pathlib.Path,
                                   expected: list):
        self.assert_exists_dir_with_given_number_of_files_in_it(dir_path,
                                                                len(expected))
        self.assert_dir_contains_at_least(dir_path, expected)

    def assert_dir_contains_at_least(self,
                                     dir_path: pathlib.Path,
                                     expected: list):
        for file_system_element in expected:
            if isinstance(file_system_element, file_structure.File):
                self.assert_dir_contains_file(dir_path, file_system_element)
            elif isinstance(file_system_element, file_structure.Link):
                self.assert_dir_contains_symlink(dir_path, file_system_element)
            elif isinstance(file_system_element, file_structure.Dir):
                self.assert_dir_matches_exactly(dir_path / file_system_element.file_name,
                                                file_system_element.file_system_element_contents)

    def _msg(self, message: str) -> str:
        return assert_utils.assertion_message(message, self.message_header)

    def assert_dir_contains_file(self,
                                 dir_path: pathlib.Path,
                                 file: file_structure.File):
        path = dir_path / file.file_name
        self.assert_exists_plain_file(path)
        self.assert_file_contents(path, file.contents)

    def assert_dir_contains_symlink(self,
                                    dir_path: pathlib.Path,
                                    sym_link: file_structure.Link):
        raise NotImplementedError()
