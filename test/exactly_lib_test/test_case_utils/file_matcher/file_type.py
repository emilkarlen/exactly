import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, sym_link, empty_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileType)


class TestFileType(unittest.TestCase):
    def _check(self,
               file_type_to_check_for: FileType,
               expected_result: bool,
               base_name_of_file_to_check: str,
               dir_contents: DirContents):
        matcher_to_check = sut.FileMatcherType(file_type_to_check_for)
        self.assertIsInstance(matcher_to_check.option_description,
                              str,
                              'option_description')
        # ACT #
        with tmp_dir(dir_contents) as tmp_dir_path:
            file_path_to_check = tmp_dir_path / base_name_of_file_to_check

            actual_result = matcher_to_check.matches(file_path_to_check)

            # ASSERT #

            self.assertEqual(file_type_to_check_for,
                             matcher_to_check.file_type,
                             'file type')

            self.assertEqual(expected_result,
                             actual_result,
                             'result')

    def test_regular(self):
        file_to_check = 'file-to-check.txt'
        cases = [
            NameAndValue('match',
                         (
                             DirContents([empty_file(file_to_check)]),
                             True,
                         )),
            NameAndValue('match: symlink to regular',
                         (
                             DirContents([empty_file('the file.txt'),
                                          sym_link(file_to_check, 'the file.txt')]),
                             True,
                         )),
            NameAndValue('not match: actual is directory',
                         (
                             DirContents([empty_dir(file_to_check)]),
                             False,
                         )),
            NameAndValue('not match: actual is broken symlink',
                         (
                             DirContents([empty_file('the file.txt'),
                                          sym_link(file_to_check, 'name-of-non-existing-file')]),
                             False,
                         )),
        ]
        for case in cases:
            dir_contents, expected_result = case.value
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.REGULAR,
                            expected_result=expected_result,
                            base_name_of_file_to_check=file_to_check,
                            dir_contents=dir_contents)

    def test_directory(self):
        dir_to_check = 'dir-to-check'
        cases = [
            NameAndValue('match',
                         (
                             DirContents([empty_dir(dir_to_check)]),
                             True,
                         )),
            NameAndValue('match: symlink to directory',
                         (
                             DirContents([empty_dir('the dir'),
                                          sym_link(dir_to_check, 'the dir')]),
                             True,
                         )),
            NameAndValue('not match: actual is regular',
                         (
                             DirContents([empty_file(dir_to_check)]),
                             False,
                         )),
            NameAndValue('not match: actual is broken symlink',
                         (
                             DirContents([empty_file('the file.txt'),
                                          sym_link(dir_to_check, 'name-of-non-existing-file')]),
                             False,
                         )),
        ]
        for case in cases:
            dir_contents, expected_result = case.value
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.DIRECTORY,
                            expected_result=expected_result,
                            base_name_of_file_to_check=dir_to_check,
                            dir_contents=dir_contents)

    def test_symlink(self):
        link_target = 'link-target-file'
        file_to_check = 'file-to-check'
        cases = [
            NameAndValue('match: symlink to regular',
                         (
                             DirContents([empty_file(link_target),
                                          sym_link(file_to_check, link_target)]),
                             True,
                         )),
            NameAndValue('match: symlink to directory',
                         (
                             DirContents([empty_dir(link_target),
                                          sym_link(file_to_check, link_target)]),
                             True,
                         )),
            NameAndValue('match: broken symlink',
                         (
                             DirContents([sym_link(file_to_check, 'non-existing-target-file')]),
                             True,
                         )),
            NameAndValue('not match: actual is regular',
                         (
                             DirContents([empty_file(file_to_check)]),
                             False,
                         )),
        ]
        for case in cases:
            dir_contents, expected_result = case.value
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.SYMLINK,
                            expected_result=expected_result,
                            base_name_of_file_to_check=file_to_check,
                            dir_contents=dir_contents)
