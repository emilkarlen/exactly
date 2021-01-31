"""
This module should probably be replaced by corresponding ValueAssertion in file_assertions
"""
import pathlib
import unittest
from typing import Sequence

from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, AssertionBase


class FileChecker:
    def __init__(self,
                 put: unittest.TestCase,
                 message_header: str = None):
        self.put = put
        self.message_header = message_header
        self.message_builder = asrt.new_message_builder(message_header)

    def assert_is_existing_empty_dir(self, p: pathlib.Path):
        self.assert_exists_dir_with_given_number_of_files_in_it(p, 0)

    def assert_exists_dir_with_given_number_of_files_in_it(
            self,
            p: pathlib.Path,
            expected_number_of_files: int,
            expected_file_system_elements: Sequence[FileSystemElement] = None):

        self.assert_exists_dir(p)
        directory_contents = list(p.iterdir())
        expected_file_names = ''
        if expected_file_system_elements is not None:
            expected_file_names = str([fse.name for fse in expected_file_system_elements])
        self.put.assertEqual(
            expected_number_of_files,
            len(directory_contents),
            self._msg('The directory "{dir}"\n'
                      'should contain exactly {expected_num_files} files {expected_file_names}\n'
                      'Found {actual_num_files} {actual_file_names}'.format(
                dir=str(p),
                expected_num_files=expected_number_of_files,
                expected_file_names=expected_file_names,
                actual_num_files=str(len(directory_contents)),
                actual_file_names=str(directory_contents))))

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
        return self.assert_dir_matches_exactly(dir_path, expected.file_system_elements)

    def assert_dir_matches_exactly(self,
                                   dir_path: pathlib.Path,
                                   expected: Sequence[FileSystemElement]):
        self.assert_exists_dir_with_given_number_of_files_in_it(dir_path,
                                                                len(expected),
                                                                expected_file_system_elements=expected)
        self.assert_dir_contains_at_least(dir_path, expected)

    def assert_dir_contains_at_least(self,
                                     dir_path: pathlib.Path,
                                     expected: Sequence[FileSystemElement]):
        for file_system_element in expected:
            if isinstance(file_system_element, file_structure.File):
                self.assert_dir_contains_file(dir_path, file_system_element)
            elif isinstance(file_system_element, file_structure.Link):
                self.assert_dir_contains_symlink(dir_path, file_system_element)
            elif isinstance(file_system_element, file_structure.Dir):
                self.assert_dir_matches_exactly(dir_path / file_system_element.file_name,
                                                file_system_element.file_system_element_contents)

    def _msg(self, message: str) -> str:
        return self.message_builder.for_sub_component(message).apply('')

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


def file_does_not_exist() -> Assertion[pathlib.Path]:
    return _FileDoesNotExist()


class _FileDoesNotExist(AssertionBase[pathlib.Path]):
    def _apply(self,
               put: unittest.TestCase,
               value: pathlib.Path,
               message_builder: MessageBuilder):
        put.assertFalse(value.exists(),
                        message_builder.msg_for_sub_component('exists'))
