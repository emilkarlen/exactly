import unittest
from pathlib import PurePosixPath
from typing import Sequence

from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx, \
    FileSpecAbsStx
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import regular_file_spec, \
    FileContentsEmptyAbsStx, FileContentsExplicitAbsStx, dir_spec, \
    DirContentsEmptyAbsStx, DirContentsExplicitAbsStx
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ExecutionExpectation, arrangement_w_tcds, \
    Expectation, ParseExpectation
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFileMustNotExist),
        unittest.makeSuite(TestFileMustExist),
    ])


IS_AT_END_OF_1ST_LNE = ParseExpectation(
    source=asrt_source.is_at_end_of_line(1),
)


class TestFileMustNotExist(unittest.TestCase):
    def test_existing_file_of_invalid_type(self):
        file_name = 'destination.txt'
        for file_spec_case in file_must_not_exist_source_cases(file_name):
            for dir_contents_case in file_must_not_exist(file_name):
                with self.subTest(
                        file_spec=file_spec_case.name,
                        dir_contents=dir_contents_case.name):
                    integration_check.CHECKER.check__abs_stx(
                        self,
                        LiteralFilesSourceAbsStx([file_spec_case.value]),
                        dir_contents_case.value,
                        arrangement_w_tcds(),
                        Expectation(
                            parse=IS_AT_END_OF_1ST_LNE,
                            execution=ExecutionExpectation(
                                is_hard_error=asrt_text_doc.is_any_text(),
                            )
                        ),
                    )

    def test_illegal_path_with_regular_file_as_dir_component(self):
        # ARRANGE #
        existing_regular_file = fs.File.empty('regular-file')
        file_name = str(PurePosixPath(existing_regular_file.name, 'destination'))
        for file_spec_case in file_must_not_exist_source_cases(file_name):
            with self.subTest(file_spec=file_spec_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx([file_spec_case.value]),
                    [existing_regular_file],
                    arrangement_w_tcds(),
                    Expectation(
                        parse=IS_AT_END_OF_1ST_LNE,
                        execution=ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text(),
                        )
                    ),
                )

    def test_broken_symlink(self):
        # ARRANGE #
        broken_sym_link = fs.sym_link('broken-symlink', 'non-existing-target')
        file_name = str(PurePosixPath(broken_sym_link.name))
        for file_spec_case in file_must_not_exist_source_cases(file_name):
            with self.subTest(file_spec=file_spec_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx([file_spec_case.value]),
                    [broken_sym_link],
                    arrangement_w_tcds(),
                    Expectation(
                        parse=IS_AT_END_OF_1ST_LNE,
                        execution=ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text(),
                        )
                    ),
                )


class TestFileMustExist(unittest.TestCase):
    def test_regular_file(self):
        file_name = 'destination.txt'
        file_name_syntax = StringLiteralAbsStx(file_name, QuoteType.HARD)
        explicit_file_contents = str_src_abs_stx.StringSourceOfStringAbsStx(
            StringLiteralAbsStx.empty_string()
        )
        file_spec_syntax = regular_file_spec(
            file_name_syntax,
            FileContentsExplicitAbsStx(ModificationType.APPEND,
                                       explicit_file_contents),
        )
        for dir_contents_case in file_must_exist_as_regular(file_name):
            with self.subTest(dir_contents=dir_contents_case.name):
                integration_check.CHECKER.check__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx([file_spec_syntax]),
                    dir_contents_case.value,
                    arrangement_w_tcds(),
                    Expectation(
                        parse=IS_AT_END_OF_1ST_LNE,
                        execution=ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text(),
                        )
                    ),
                )

    def test_dir(self):
        file_name = 'destination'
        file_name_syntax = StringLiteralAbsStx(file_name, QuoteType.HARD)
        explicit_dir_contents = LiteralFilesSourceAbsStx(())
        file_spec_syntax = dir_spec(
            file_name_syntax,
            DirContentsExplicitAbsStx(ModificationType.APPEND,
                                      explicit_dir_contents),
        )
        for dir_contents_case in file_must_exist_as_dir(file_name):
            with self.subTest(dir_contents=dir_contents_case.name):
                integration_check.CHECKER.check__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx([file_spec_syntax]),
                    dir_contents_case.value,
                    arrangement_w_tcds(),
                    Expectation(
                        parse=IS_AT_END_OF_1ST_LNE,
                        execution=ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text(),
                        )
                    ),
                )

    def test_illegal_path_with_regular_file_as_dir_component(self):
        # ARRANGE #
        existing_regular_file = fs.File.empty('regular-file')
        file_name = str(PurePosixPath(existing_regular_file.name, 'destination'))

        file_name_syntax = StringLiteralAbsStx(file_name, QuoteType.HARD)

        explicit_file_contents = str_src_abs_stx.StringSourceOfStringAbsStx(
            StringLiteralAbsStx.empty_string()
        )
        file_spec_cases = [
            NameAndValue(
                'regular',
                regular_file_spec(
                    file_name_syntax,
                    FileContentsExplicitAbsStx(ModificationType.APPEND,
                                               explicit_file_contents),
                ),
            ),
            NameAndValue(
                'dir',
                dir_spec(
                    file_name_syntax,
                    DirContentsExplicitAbsStx(ModificationType.APPEND,
                                              LiteralFilesSourceAbsStx(())),
                ),
            ),
        ]
        for file_spec_case in file_spec_cases:
            with self.subTest(file_spec=file_spec_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx(
                    self,
                    LiteralFilesSourceAbsStx([file_spec_case.value]),
                    [existing_regular_file],
                    arrangement_w_tcds(),
                    Expectation(
                        parse=IS_AT_END_OF_1ST_LNE,
                        execution=ExecutionExpectation(
                            is_hard_error=asrt_text_doc.is_any_text(),
                        )
                    ),
                )


def file_must_not_exist_source_cases(file_name: str) -> Sequence[NameAndValue[FileSpecAbsStx]]:
    file_name_syntax = StringLiteralAbsStx(file_name, QuoteType.HARD)

    explicit_file_contents = str_src_abs_stx.StringSourceOfStringAbsStx(
        StringLiteralAbsStx.empty_string()
    )
    explicit_dir_contents = LiteralFilesSourceAbsStx(())

    return [
        NameAndValue(
            'regular / implicit empty',
            regular_file_spec(file_name_syntax,
                              FileContentsEmptyAbsStx()),
        ),
        NameAndValue(
            'regular / explicit creation',
            regular_file_spec(file_name_syntax,
                              FileContentsExplicitAbsStx(ModificationType.CREATE,
                                                         explicit_file_contents)),
        ),
        NameAndValue(
            'dir / implicit empty',
            dir_spec(file_name_syntax,
                     DirContentsEmptyAbsStx()),
        ),
        NameAndValue(
            'dir / explicit creation',
            dir_spec(file_name_syntax,
                     DirContentsExplicitAbsStx(ModificationType.CREATE,
                                               explicit_dir_contents)),
        ),
    ]


def file_must_not_exist(file_name: str) -> Sequence[NameAndValue[FileSystemElements]]:
    return [
        NameAndValue(
            'exists as regular',
            [fs.File.empty(file_name)],
        ),
        NameAndValue(
            'exists as dir',
            [fs.Dir.empty(file_name)],
        ),
        NameAndValue(
            'exists as sym-link to regular',
            [fs.File.empty('a-regular'),
             fs.sym_link(file_name, 'a-regular')],
        ),
        NameAndValue(
            'exists as sym-link to dir',
            [fs.Dir.empty('a-dir'),
             fs.sym_link(file_name, 'a-dir')],
        ),
    ]


def file_must_exist_as_regular_source_cases(file_name: str) -> Sequence[NameAndValue[FileSpecAbsStx]]:
    file_name_syntax = StringLiteralAbsStx(file_name, QuoteType.HARD)

    explicit_file_contents = str_src_abs_stx.StringSourceOfStringAbsStx(
        StringLiteralAbsStx.empty_string()
    )
    explicit_dir_contents = LiteralFilesSourceAbsStx(())

    return [
        NameAndValue(
            'regular / explicit append',
            regular_file_spec(file_name_syntax,
                              FileContentsExplicitAbsStx(ModificationType.CREATE,
                                                         explicit_file_contents)),
        ),
        NameAndValue(
            'dir / implicit empty',
            dir_spec(file_name_syntax,
                     DirContentsEmptyAbsStx()),
        ),
        NameAndValue(
            'dir / explicit creation',
            dir_spec(file_name_syntax,
                     DirContentsExplicitAbsStx(ModificationType.CREATE,
                                               explicit_dir_contents)),
        ),
    ]


def file_must_exist_as_regular(file_name: str) -> Sequence[NameAndValue[FileSystemElements]]:
    return [
        NameAndValue(
            'do not exist',
            [],
        ),
        NameAndValue(
            'exists as dir',
            [fs.Dir.empty(file_name)],
        ),
        NameAndValue(
            'exists as sym-link to dir',
            [fs.Dir.empty('a-dir'),
             fs.sym_link(file_name, 'a-dir')],
        ),
        NameAndValue(
            'broken sym-link',
            [fs.sym_link(file_name, 'non-existing')],
        ),
    ]


def file_must_exist_as_dir(file_name: str) -> Sequence[NameAndValue[FileSystemElements]]:
    return [
        NameAndValue(
            'do not exist',
            [],
        ),
        NameAndValue(
            'exists as regular',
            [fs.File.empty(file_name)],
        ),
        NameAndValue(
            'exists as sym-link to regular',
            [fs.File.empty('a-regular'),
             fs.sym_link(file_name, 'a-regular')],
        ),
        NameAndValue(
            'broken sym-link',
            [fs.sym_link(file_name, 'non-existing')],
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
