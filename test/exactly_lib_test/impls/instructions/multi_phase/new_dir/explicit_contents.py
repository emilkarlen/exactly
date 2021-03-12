import unittest
from typing import Sequence

from exactly_lib.impls.instructions.multi_phase import new_dir as sut
from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.abstract_syntax import NewDirArguments
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.assertions import is_failure
from exactly_lib_test.impls.instructions.multi_phase.test_resources import embryo_arr_exp
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opts
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.type_val_deps.types.files_source.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import DefaultRelPathAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingValidation(),
        TestSuccessfulContentsFromFilesSource(),
        TestFailingContentsFromFilesSource(),
    ])


class TestFailingValidation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        dst_path = DefaultRelPathAbsStx('non-existing-dir')

        for modification in fs_abs_stx.ModificationType:
            for validation_case in validation_cases.failing_validation_cases():
                instruction_syntax = NewDirArguments(
                    dst_path,
                    fs_abs_stx.DirContentsExplicitAbsStx(modification,
                                                         validation_case.value.syntax),
                )
                # ACT & ASSERT #
                _CHECKER.check__abs_stx__std_layouts_and_source_variants(
                    self,
                    instruction_syntax,
                    embryo_arr_exp.Arrangement.phase_agnostic(
                        symbols=validation_case.value.symbol_context.symbol_table,
                    ),
                    embryo_arr_exp.MultiSourceExpectation.phase_agnostic(
                        validation=validation_case.value.assertion,
                        symbol_usages=validation_case.value.symbol_context.usages_assertion,
                    ),
                    sub_test_identifiers={
                        'modification': modification,
                        'validation': validation_case.name
                    },
                )


class ContentsCase:
    def __init__(self,
                 name: str,
                 dst_file_name: str,
                 contents_syntax: fs_abs_stx.DirContentsAbsStx,
                 pre_existing_files: FileSystemElements,
                 expected_files: FileSystemElements = (),
                 ):
        self.name = name
        self.dst_file_name = dst_file_name
        self.contents_syntax = contents_syntax
        self.pre_existing_files = pre_existing_files
        self.expected_files = expected_files


class TestSuccessfulContentsFromFilesSource(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)
        for case in successful_cases():
            dst_path = rel_conf.path_abs_stx_of_name(case.dst_file_name)
            instruction_syntax = NewDirArguments(
                dst_path,
                case.contents_syntax,
            )
            with self.subTest(case.name):
                # ACT & ASSERT #
                _CHECKER.check__abs_stx(
                    self,
                    instruction_syntax,
                    embryo_arr_exp.Arrangement.phase_agnostic(
                        tcds=TcdsArrangement(
                            non_hds_contents=rel_conf.populator_for_relativity_option_root__non_hds__s(
                                case.pre_existing_files
                            )
                        ),
                    ),
                    embryo_arr_exp.Expectation.phase_agnostic(
                        main_side_effects_on_sds=rel_conf.assert_root_dir_contains_exactly__p(
                            case.expected_files)
                    ),
                )


class TestFailingContentsFromFilesSource(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)
        for case in _failing_cases():
            dst_path = rel_conf.path_abs_stx_of_name(case.dst_file_name)
            instruction_syntax = NewDirArguments(
                dst_path,
                case.contents_syntax,
            )
            with self.subTest(case.name):
                # ACT & ASSERT #
                _CHECKER.check__abs_stx(
                    self,
                    instruction_syntax,
                    embryo_arr_exp.Arrangement.phase_agnostic(
                        tcds=TcdsArrangement(
                            non_hds_contents=rel_conf.populator_for_relativity_option_root__non_hds__s(
                                case.pre_existing_files
                            )
                        ),
                    ),
                    embryo_arr_exp.Expectation.phase_agnostic(
                        main_result=is_failure()
                    )
                )


def successful_cases() -> Sequence[ContentsCase]:
    return [
        _successful__create(),
        _successful__append(),
    ]


def _failing_cases() -> Sequence[ContentsCase]:
    existing_dir = fs.Dir.empty('existing')
    return [
        ContentsCase(
            'create',
            existing_dir.name,
            fs_abs_stx.DirContentsExplicitAbsStx(
                ModificationType.CREATE,
                fs_abs_stx.LiteralFilesSourceAbsStx(())
            ),
            pre_existing_files=[existing_dir],
        ),
        ContentsCase(
            'append',
            existing_dir.name,
            fs_abs_stx.DirContentsExplicitAbsStx(
                ModificationType.APPEND,
                fs_abs_stx.LiteralFilesSourceAbsStx(())
            ),
            pre_existing_files=[],
        ),
    ]


def _successful__create() -> ContentsCase:
    created_file = fs.File.empty('created-regular-file')
    created_dir = fs.Dir('created-dir', [
        created_file,
    ])

    return ContentsCase(
        'create',
        created_dir.name,
        fs_abs_stx.DirContentsExplicitAbsStx(
            ModificationType.CREATE,
            fs_abs_stx.LiteralFilesSourceAbsStx([
                fs_abs_stx.regular_file_spec__str_name(
                    created_file.name,
                    fs_abs_stx.FileContentsEmptyAbsStx(),
                )
            ])
        ),
        pre_existing_files=(),
        expected_files=[created_dir]
    )


def _successful__append() -> ContentsCase:
    created_file = fs.File.empty('created-regular-file')
    dst_dir = fs.Dir('destination-dir', [
        created_file,
    ])

    return ContentsCase(
        'create',
        dst_dir.name,
        fs_abs_stx.DirContentsExplicitAbsStx(
            ModificationType.APPEND,
            fs_abs_stx.LiteralFilesSourceAbsStx([
                fs_abs_stx.regular_file_spec__str_name(
                    created_file.name,
                    fs_abs_stx.FileContentsEmptyAbsStx(),
                )
            ])
        ),
        pre_existing_files=[fs.Dir.empty(dst_dir.name)],
        expected_files=[dst_dir]
    )


_CHECKER = embryo_check.Checker(sut.EmbryoParser())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
