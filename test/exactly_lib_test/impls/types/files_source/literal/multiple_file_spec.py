import unittest
from pathlib import PurePosixPath

from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ExecutionExpectation, \
    MultiSourceExpectation
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestDirFollowedByRegular(),
        TestRegularFollowedByDir(),
    ])


class TestDirFollowedByRegular(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        dir_name = 'the-dir'
        file_in_dir_name = 'the-file'
        appended_file_contents = 'appended file contents'

        spec_that_creates_dir_with_file = abs_stx.dir_spec(
            file_name_arg(dir_name),
            abs_stx.DirContentsExplicitAbsStx(
                ModificationType.CREATE,
                abs_stx.LiteralFilesSourceAbsStx([
                    abs_stx.regular_file_spec(
                        file_name_arg(file_in_dir_name),
                        abs_stx.FileContentsEmptyAbsStx()
                    )
                ])
            )
        )
        spec_that_appends_to_file_in_dir__requiring_file_exists = abs_stx.regular_file_spec(
            file_name_arg(str(PurePosixPath(dir_name, file_in_dir_name))),
            abs_stx.FileContentsExplicitAbsStx(
                ModificationType.APPEND,
                str_src_of_str(appended_file_contents)
            )
        )

        syntax_with_list_of_file_specs = LiteralFilesSourceAbsStx([
            spec_that_creates_dir_with_file,
            spec_that_appends_to_file_in_dir__requiring_file_exists,
        ])
        expected_contents = [
            fs.Dir(dir_name, [
                fs.File(file_in_dir_name, appended_file_contents)
            ])
        ]
        integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
            self,
            syntax_with_list_of_file_specs,
            (),
            arrangement_w_tcds(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    main_result=asrt_fs.dir_contains_exactly_2(expected_contents)
                )
            )
        )


class TestRegularFollowedByDir(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        dir_name = 'the-dir'
        file_in_dir_name = 'the-file'

        spec_that_creates_file_in_sub_dir = abs_stx.regular_file_spec(
            file_name_arg(str(PurePosixPath(dir_name, file_in_dir_name))),
            abs_stx.FileContentsEmptyAbsStx()
        )

        spec_that_appends_to_dir__requiring_dir_exists = abs_stx.dir_spec(
            file_name_arg(dir_name),
            abs_stx.DirContentsExplicitAbsStx(
                ModificationType.APPEND,
                LiteralFilesSourceAbsStx(())
            )
        )

        syntax_with_list_of_file_specs = LiteralFilesSourceAbsStx([
            spec_that_creates_file_in_sub_dir,
            spec_that_appends_to_dir__requiring_dir_exists,
        ])
        expected_contents = [
            fs.Dir(dir_name, [
                fs.File.empty(file_in_dir_name)
            ])
        ]
        # ACT & ASSERT #
        integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
            self,
            syntax_with_list_of_file_specs,
            (),
            arrangement_w_tcds(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    main_result=asrt_fs.dir_contains_exactly_2(expected_contents)
                )
            )
        )


def file_name_arg(file_name: str) -> StringLiteralAbsStx:
    return StringLiteralAbsStx(file_name, QuoteType.HARD)


def str_src_of_str(contents: str) -> str_src_abs_stx.StringSourceAbsStx:
    return str_src_abs_stx.StringSourceOfStringAbsStx.of_str(contents, QuoteType.HARD)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
