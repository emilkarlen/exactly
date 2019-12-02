import unittest

from exactly_lib.test_case_utils.file_matcher import parse_file_matcher as sut
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check, model_construction
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, sym_link, empty_dir
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileType)


class TestFileType(unittest.TestCase):
    def _check(self,
               file_type_to_check_for: FileType,
               expected_result: bool,
               base_name_of_file_to_check: str,
               dir_contents: DirContents):

        # ACT #
        integration_check.check_equivalent_source_variants__for_expression_parser(
            self,
            sut.parser(),
            ArgumentElements(arg.Type(file_type_to_check_for).elements).as_arguments,
            model_construction.constant_relative_file_name(base_name_of_file_to_check),
            ArrangementPostAct(
                non_hds_contents=sds_populator.cwd_contents(dir_contents),
            ),
            matcher_assertions.expectation(
                main_result=asrt_matching_result.matches_value(expected_result),
            )
        )

    def test_regular(self):
        file_to_check = 'file-to-check.txt'
        cases = [
            NEA('match',
                True,
                DirContents([empty_file(file_to_check)]),
                ),
            NEA('match: symlink to regular',
                True,
                DirContents([empty_file('the file.txt'),
                             sym_link(file_to_check, 'the file.txt')]),
                ),
            NEA('not match: actual is directory',
                False,
                DirContents([empty_dir(file_to_check)]),
                ),
            NEA('not match: actual is broken symlink',
                False,
                DirContents([empty_file('the file.txt'),
                             sym_link(file_to_check, 'name-of-non-existing-file')]),
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.REGULAR,
                            expected_result=case.expected,
                            base_name_of_file_to_check=file_to_check,
                            dir_contents=case.actual)

    def test_directory(self):
        dir_to_check = 'dir-to-check'
        cases = [
            NEA('match',
                True,
                DirContents([empty_dir(dir_to_check)]),
                ),
            NEA('match: symlink to directory',
                True,
                DirContents([empty_dir('the dir'),
                             sym_link(dir_to_check, 'the dir')]),
                ),
            NEA('not match: actual is regular',
                False,
                DirContents([empty_file(dir_to_check)]),
                ),
            NEA('not match: actual is broken symlink',
                False,
                DirContents([empty_file('the file.txt'),
                             sym_link(dir_to_check, 'name-of-non-existing-file')]),
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.DIRECTORY,
                            expected_result=case.expected,
                            base_name_of_file_to_check=dir_to_check,
                            dir_contents=case.actual)

    def test_symlink(self):
        link_target = 'link-target-file'
        file_to_check = 'file-to-check'
        cases = [
            NEA('match: symlink to regular',
                True,
                DirContents([empty_file(link_target),
                             sym_link(file_to_check, link_target)]),
                ),
            NEA('match: symlink to directory',
                True,
                DirContents([empty_dir(link_target),
                             sym_link(file_to_check, link_target)]),
                ),
            NEA('match: broken symlink',
                True,
                DirContents([sym_link(file_to_check, 'non-existing-target-file')]),
                ),
            NEA('not match: actual is regular',
                False,
                DirContents([empty_file(file_to_check)]),
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.SYMLINK,
                            expected_result=case.expected,
                            base_name_of_file_to_check=file_to_check,
                            dir_contents=case.actual)
