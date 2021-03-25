import unittest

from exactly_lib.impls.file_properties import FileType
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as arg
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    ExecutionExpectation, \
    Expectation
from exactly_lib_test.tcfs.test_resources import non_hds_populator
from exactly_lib_test.test_resources.arguments.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.files.file_structure import DirContents, sym_link, File, Dir
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileType)


class TestFileType(unittest.TestCase):
    def _check(self,
               file_type_to_check_for: FileType,
               expected_result: bool,
               base_name_of_file_to_check: str,
               dir_contents: DirContents):

        # ACT #
        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            ArgumentElements(arg.Type(file_type_to_check_for).elements).as_arguments,
            integration_check.constant_relative_file_name(base_name_of_file_to_check),
            arrangement_w_tcds(
                non_hds_contents=non_hds_populator.rel_option(RelNonHdsOptionType.REL_CWD, dir_contents),
            ),
            Expectation(
                execution=ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(expected_result),
                ),
            )
        )

    def test_regular(self):
        file_to_check = 'file-to-check.txt'
        cases = [
            NEA('match',
                True,
                DirContents([File.empty(file_to_check)]),
                ),
            NEA('match: symlink to regular',
                True,
                DirContents([File.empty('the file.txt'),
                             sym_link(file_to_check, 'the file.txt')]),
                ),
            NEA('not match: actual is directory',
                False,
                DirContents([Dir.empty(file_to_check)]),
                ),
            NEA('not match: actual is broken symlink',
                False,
                DirContents([File.empty('the file.txt'),
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
                DirContents([Dir.empty(dir_to_check)]),
                ),
            NEA('match: symlink to directory',
                True,
                DirContents([Dir.empty('the dir'),
                             sym_link(dir_to_check, 'the dir')]),
                ),
            NEA('not match: actual is regular',
                False,
                DirContents([File.empty(dir_to_check)]),
                ),
            NEA('not match: actual is broken symlink',
                False,
                DirContents([File.empty('the file.txt'),
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
                DirContents([File.empty(link_target),
                             sym_link(file_to_check, link_target)]),
                ),
            NEA('match: symlink to directory',
                True,
                DirContents([Dir.empty(link_target),
                             sym_link(file_to_check, link_target)]),
                ),
            NEA('match: broken symlink',
                True,
                DirContents([sym_link(file_to_check, 'non-existing-target-file')]),
                ),
            NEA('not match: actual is regular',
                False,
                DirContents([File.empty(file_to_check)]),
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(file_type_to_check_for=FileType.SYMLINK,
                            expected_result=case.expected,
                            base_name_of_file_to_check=file_to_check,
                            dir_contents=case.actual)
