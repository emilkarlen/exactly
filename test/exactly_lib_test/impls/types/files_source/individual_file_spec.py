import unittest
from pathlib import PurePosixPath
from typing import Sequence, Callable

from exactly_lib.impls.types.files_source.defs import FileType, ModificationType
from exactly_lib.util import functional
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx, \
    ContentsAbsStx
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ExecutionExpectation, \
    MultiSourceExpectation
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, FileSystemElements
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestCreate(),
        unittest.makeSuite(TestAppend),
    ])


class TestCreate(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        leaf_file_name = 'created-leaf'
        for create_path_case in create_path_cases(leaf_file_name):
            for rel_file_name_case in rel_file_name_cases__create(
                    leaf_file_name,
                    create_path_case.expected_created_file):
                syntax = LiteralFilesSourceAbsStx([
                    abs_stx.FileSpecAbsStx.of_file_type(
                        create_path_case.file_type,
                        file_name_arg(str(rel_file_name_case.file_spec_file_name)),
                        create_path_case.contents__syntax,
                    )
                ])
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                    self,
                    syntax,
                    rel_file_name_case.arrangement,
                    arrangement_w_tcds(),
                    MultiSourceExpectation(
                        execution=ExecutionExpectation(
                            main_result=asrt_fs.dir_contains_exactly_2(
                                rel_file_name_case.expected_root_dir_contents
                            )
                        )
                    ),
                    sub_test_identifiers={
                        'create_case': create_path_case.name,
                        'rel_file_name_case': rel_file_name_case.name,
                    }
                )


class TestAppend(unittest.TestCase):
    def test_regular(self):
        # ARRANGE #
        to_append__text = '<appended text>'
        non_empty_original__text = '<original text>'

        append_contents_syntax = abs_stx.FileContentsExplicitAbsStx(
            ModificationType.APPEND,
            str_src_abs_stx.StringSourceOfStringAbsStx.of_str(
                to_append__text, QuoteType.HARD,
            )
        )
        name_of_modified_file = 'destination.txt'

        contents_cases: Sequence[AppendRegularContentsCase] = [
            AppendRegularContentsCase(
                'empty',
                '',
                to_append__text,
            ),
            AppendRegularContentsCase(
                'non-empty',
                non_empty_original__text,
                non_empty_original__text + to_append__text,
            ),
        ]
        for target_location_case in target_locations():
            syntax = abs_stx.LiteralFilesSourceAbsStx([
                abs_stx.regular_file_spec(
                    file_name_arg(target_location_case.target_rel_path(name_of_modified_file)),
                    append_contents_syntax,
                )
            ])
            for contents_case in contents_cases:
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                    self,
                    syntax,
                    [
                        target_location_case.file_for_leaf(
                            contents_case.original(name_of_modified_file)
                        )
                    ],
                    arrangement_w_tcds(),
                    MultiSourceExpectation(
                        execution=ExecutionExpectation(
                            main_result=asrt_fs.dir_contains_exactly_2([
                                target_location_case.file_for_leaf(
                                    fs.File(name_of_modified_file,
                                            contents_case.expected_contents_after_modification)
                                )
                            ])
                        )
                    ),
                    sub_test_identifiers={
                        'contents': contents_case.name,
                        'target_location': target_location_case.name
                    }
                )

    def test_dir(self):
        # ARRANGE #
        to_append_file = fs.File('file-to-append', 'contents of file to append')
        pre_existing_file = fs.File('pre-existing', 'contents of pre existing file')

        append_single_file__contents_syntax = abs_stx.DirContentsExplicitAbsStx(
            ModificationType.APPEND,
            abs_stx.LiteralFilesSourceAbsStx([
                abs_stx.regular_file_spec(
                    file_name_arg(to_append_file.name),
                    abs_stx.FileContentsExplicitAbsStx(
                        ModificationType.CREATE,
                        str_src_abs_stx.StringSourceOfStringAbsStx.of_str(to_append_file.contents,
                                                                          QuoteType.HARD)
                    )
                )
            ])
        )
        target_dir_name = 'destination-dir'

        contents_cases: Sequence[AppendDirContentsCase] = [
            AppendDirContentsCase(
                'empty',
                [],
                [to_append_file],
            ),
            AppendDirContentsCase(
                'non-empty',
                [pre_existing_file],
                [pre_existing_file, to_append_file],
            ),
        ]
        for target_location_case in target_locations():
            syntax = abs_stx.LiteralFilesSourceAbsStx([
                abs_stx.dir_spec(
                    file_name_arg(target_location_case.target_rel_path(target_dir_name)),
                    append_single_file__contents_syntax,
                )
            ])
            for contents_case in contents_cases:
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx__layout__std_source_variants(
                    self,
                    syntax,
                    [
                        target_location_case.file_for_leaf(
                            contents_case.original(target_dir_name)
                        )
                    ],
                    arrangement_w_tcds(),
                    MultiSourceExpectation(
                        execution=ExecutionExpectation(
                            main_result=asrt_fs.dir_contains_exactly_2([
                                target_location_case.file_for_leaf(
                                    fs.Dir(target_dir_name,
                                           contents_case.expected_contents_after_modification)
                                )
                            ])
                        )
                    ),
                    sub_test_identifiers={
                        'contents': contents_case.name,
                        'target_location': target_location_case.name
                    }
                )


class TargetLocationCase:
    def __init__(self,
                 name: str,
                 get_target_rel_path: Callable[[str], str],
                 get_file_with_original: Callable[[FileSystemElement], FileSystemElement],
                 ):
        self.name = name
        self.get_target_rel_path = get_target_rel_path
        self.get_file_with_original = get_file_with_original

    def target_rel_path(self, target_leaf_name: str) -> str:
        return self.get_target_rel_path(target_leaf_name)

    def file_for_leaf(self, original_target: FileSystemElement) -> FileSystemElement:
        return self.get_file_with_original(original_target)


def target_locations() -> Sequence[TargetLocationCase]:
    sub_dir_name = 'sub-dir'
    return [
        TargetLocationCase(
            'direct (no sub dir)',
            functional.identity,
            functional.identity,
        ),
        TargetLocationCase(
            'in sub dir',
            lambda fn: str(PurePosixPath(sub_dir_name, fn)),
            lambda fse: fs.Dir(sub_dir_name, [fse]),
        ),
    ]


class AppendRegularContentsCase:
    def __init__(self,
                 name: str,
                 contents_before_modification: str,
                 expected_contents_after_modification: str,
                 ):
        self.name = name
        self.contents_before_modification = contents_before_modification
        self.expected_contents_after_modification = expected_contents_after_modification

    def original(self, file_name: str) -> FileSystemElement:
        return fs.File(file_name, self.contents_before_modification)


class AppendDirContentsCase:
    def __init__(self,
                 name: str,
                 contents_before_modification: FileSystemElements,
                 expected_contents_after_modification: FileSystemElements,
                 ):
        self.name = name
        self.contents_before_modification = contents_before_modification
        self.expected_contents_after_modification = expected_contents_after_modification

    def original(self, file_name: str) -> FileSystemElement:
        return fs.Dir(file_name, self.contents_before_modification)


class RelFileNameCase:
    def __init__(self,
                 name: str,
                 file_spec_file_name: PurePosixPath,
                 arrangement: FileSystemElements,
                 expected_root_dir_contents: FileSystemElements,
                 ):
        self.name = name
        self.file_spec_file_name = file_spec_file_name
        self.arrangement = arrangement
        self.expected_root_dir_contents = expected_root_dir_contents


def rel_file_name_cases__create(created_leaf_file_name: str,
                                expected_created_file: FileSystemElement,
                                ) -> Sequence[RelFileNameCase]:
    sub_dir_name = 'sub-dir'
    sub_sub_dir_name = 'sub-sub-dir'

    return [
        RelFileNameCase(
            'direct (no sub dirs)',
            PurePosixPath(created_leaf_file_name),
            [],
            [expected_created_file],
        ),
        RelFileNameCase(
            'in sub dir (existing)',
            PurePosixPath(sub_dir_name, created_leaf_file_name),
            [fs.Dir.empty(sub_dir_name)],
            [fs.Dir(sub_dir_name, [expected_created_file])],
        ),
        RelFileNameCase(
            'in sub dir (non-existing)',
            PurePosixPath(sub_dir_name, created_leaf_file_name),
            [],
            [fs.Dir(sub_dir_name, [expected_created_file])],
        ),
        RelFileNameCase(
            'in sub sub dir (non-existing)',
            PurePosixPath(sub_dir_name, sub_sub_dir_name, created_leaf_file_name),
            [],
            [fs.Dir(sub_dir_name,
                    [fs.Dir(sub_sub_dir_name, [expected_created_file])]
                    )
             ],
        ),
    ]


class FileSpecAndExpectedCase:
    def __init__(self,
                 name: str,
                 file_type: FileType,
                 contents__syntax: ContentsAbsStx,
                 expected_created_file: FileSystemElement,
                 ):
        self.name = name
        self.file_type = file_type
        self.contents__syntax = contents__syntax
        self.expected_created_file = expected_created_file


def create_path_cases(created_leaf_file_name: str) -> Sequence[FileSpecAndExpectedCase]:
    explicit_file_contents = 'explicit file contents'
    name_of_created_file_in_dir = 'file-in-dir.txt'
    name_of_sub_dir = 'created-sub-dir'
    file_in_created_dir__file_spec = abs_stx.regular_file_spec(
        StringLiteralAbsStx(name_of_created_file_in_dir, QuoteType.HARD),
        abs_stx.FileContentsEmptyAbsStx(),
    )
    return [
        FileSpecAndExpectedCase(
            'regular / implicit empty',
            FileType.REGULAR,
            abs_stx.FileContentsEmptyAbsStx(),
            fs.File.empty(created_leaf_file_name),
        ),
        FileSpecAndExpectedCase(
            'regular / explicit contents',
            FileType.REGULAR,
            abs_stx.FileContentsExplicitAbsStx(
                ModificationType.CREATE,
                str_src_abs_stx.StringSourceOfStringAbsStx.of_str(explicit_file_contents,
                                                                  QuoteType.HARD)
            ),
            fs.File(created_leaf_file_name, explicit_file_contents),
        ),
        FileSpecAndExpectedCase(
            'dir / implicit empty',
            FileType.DIR,
            abs_stx.DirContentsEmptyAbsStx(),
            fs.Dir.empty(created_leaf_file_name),
        ),
        FileSpecAndExpectedCase(
            'dir / explicit contents',
            FileType.DIR,
            abs_stx.DirContentsExplicitAbsStx(
                ModificationType.CREATE,
                abs_stx.LiteralFilesSourceAbsStx([
                    file_in_created_dir__file_spec
                ])
            ),
            fs.Dir(created_leaf_file_name,
                   [fs.File.empty(name_of_created_file_in_dir)]
                   ),
        ),
        FileSpecAndExpectedCase(
            'dir / explicit contents / nested dirs',
            FileType.DIR,
            abs_stx.DirContentsExplicitAbsStx(
                ModificationType.CREATE,
                abs_stx.LiteralFilesSourceAbsStx([
                    abs_stx.dir_spec(
                        file_name_arg(name_of_sub_dir),
                        abs_stx.DirContentsExplicitAbsStx(
                            ModificationType.CREATE,
                            abs_stx.LiteralFilesSourceAbsStx([
                                file_in_created_dir__file_spec,
                            ])
                        ),
                    )
                ])
            ),
            fs.Dir(created_leaf_file_name,
                   [fs.Dir(name_of_sub_dir,
                           [fs.File.empty(name_of_created_file_in_dir)]
                           )
                    ]
                   ),
        ),
    ]


def file_name_arg(file_name: str) -> StringLiteralAbsStx:
    return StringLiteralAbsStx(file_name, QuoteType.HARD)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
