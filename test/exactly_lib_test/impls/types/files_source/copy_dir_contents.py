import pathlib
import unittest
from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition, RelOptionType
from exactly_lib.type_val_prims.files_source.files_source import FilesSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check
from exactly_lib_test.impls.types.files_source.test_resources import models
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import PrimAndExeExpectation, Arrangement, \
    Expectation, ParseExpectation, ExecutionExpectation
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.tcfs.test_resources.path_relativities import RELATIVITY_VARIANTS__READ__BEFORE_ACT
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.test_resources.test_utils import NArrEx, NExArr
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_files
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.path.test_resources import references as path_references
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import CustomPathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import PathStringAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
        TestValidationShouldFailWhenSourceIsNotExistingDir(),
        TestHardErrorShouldBeRaisedWhenSourceDirContainsNameAlreadyInDestination(),
        TestSuccess(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        missing_path_argument_syntax = abs_stx.CopyOfDirContentsAbsStx(CustomPathAbsStx.empty())
        # ACT & ASSERT #
        integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
            self,
            missing_path_argument_syntax,
        )


class TestValidationShouldFailWhenSourceIsNotExistingDir(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        src_dir_name = 'source-dir'
        path_symbol = StringReferenceAbsStx('SRC_PATH_SYMBOL')
        dst_path_abs_stx = PathStringAbsStx.of_components([
            path_symbol,
            StringLiteralAbsStx(src_dir_name),
        ])
        arguments_syntax = abs_stx.CopyOfDirContentsAbsStx(dst_path_abs_stx)
        execution_cases = validation_exe_cases(src_dir_name, path_symbol.name)
        # ACT & ASSERT #
        integration_check.CHECKER.check_abs_stx__multi__w_source_variants(
            self,
            arguments_syntax,
            symbol_references=asrt.matches_singleton_sequence(
                is_src_dir_argument(path_symbol.name)
            ),
            input_=models.arbitrary(),
            execution=execution_cases,
        )


class TestHardErrorShouldBeRaisedWhenSourceDirContainsNameAlreadyInDestination(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        clashing_file_name = 'clashing-file'
        non_clashing_file_name = 'non-clashing-file'

        clash_cases: Sequence[NameAndValue[FileSystemElements]] = [
            NameAndValue(
                'exists as regular',
                [fs.File.empty(clashing_file_name)],
            ),
            NameAndValue(
                'exists as dir',
                [fs.Dir.empty(clashing_file_name)],
            ),
            NameAndValue(
                'exists as sym-link to regular',
                [fs.File.empty(non_clashing_file_name),
                 fs.sym_link(clashing_file_name, non_clashing_file_name)],
            ),
            NameAndValue(
                'exists as broken sym-link',
                [fs.sym_link(clashing_file_name, non_clashing_file_name)],
            ),
        ]
        src_dir_relativity = relativity_options.conf_rel_any(RelOptionType.REL_HDS_CASE)
        src_dir_symbol = PathDdvSymbolContext.of_no_suffix(
            'SRC_PATH_SYMBOL',
            src_dir_relativity.relativity,
            accepted_relativities=RELATIVITY_VARIANTS__READ__BEFORE_ACT,
        )
        arguments_syntax = abs_stx.CopyOfDirContentsAbsStx(src_dir_symbol.abstract_syntax)
        for clash_case in clash_cases:
            with self.subTest(clash_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check__abs_stx(
                    self,
                    arguments_syntax,
                    clash_case.value,
                    Arrangement(
                        symbols=src_dir_symbol.symbol_table,
                        tcds=TcdsArrangement(
                            tcds_contents=src_dir_relativity.populator_for_relativity_option_root__s(
                                [fs.File.empty(clashing_file_name)]
                            )
                        )
                    ),
                    Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_end_of_line(1),
                            symbol_references=src_dir_symbol.references_assertion,
                        ),
                        execution=ExecutionExpectation.is_any_hard_error()
                    ),
                )


class TestSuccess(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        pre_existing_files_cases: Sequence[NameAndValue[FileSystemElements]] = [
            NameAndValue(
                'no pre-existing files',
                [],
            ),
            NameAndValue(
                'regular file',
                [fs.File.empty('pre-exist-regular')],
            ),
            NameAndValue(
                'dir',
                [fs.Dir('pre-existing-dir', [fs.File.empty('file-in-pre-existing-dir')])],
            ),
        ]

        src_dir_contents_cases: Sequence[NameAndValue[FileSystemElements]] = [
            NameAndValue(
                'empty',
                [],
            ),
            NameAndValue(
                'single regular file',
                [fs.File.empty('regular.txt')],
            ),
            NameAndValue(
                'single dir',
                [fs.Dir.empty('a-dir')],
            ),
            NameAndValue(
                'multiple files',
                [fs.File.empty('regular.txt'),
                 fs.Dir.empty('a-dir')],
            ),
            NameAndValue(
                'dir with non-empty sub dirs',
                [fs.Dir('top-dir', [
                    fs.File.empty('file-in-top-dir'),
                    fs.Dir('dir-in-top-dir', [
                        fs.File('file-in-sub-dir.txt', 'file contents'),
                        fs.Dir.empty('dir-in-sub-dir'),
                    ]),
                ])],
            ),
        ]
        src_dir_relativity = relativity_options.conf_rel_any(RelOptionType.REL_HDS_CASE)
        src_dir_symbol = PathDdvSymbolContext.of_no_suffix(
            'SRC_PATH_SYMBOL',
            src_dir_relativity.relativity,
            accepted_relativities=RELATIVITY_VARIANTS__READ__BEFORE_ACT,
        )
        arguments_syntax = abs_stx.CopyOfDirContentsAbsStx(src_dir_symbol.abstract_syntax)
        for pre_existing_files_case in pre_existing_files_cases:
            for src_dir_contents_case in src_dir_contents_cases:
                with self.subTest(pre_existing=pre_existing_files_case.name,
                                  src_dir_contents=src_dir_contents_case.name):
                    # ACT & ASSERT #
                    integration_check.CHECKER.check__abs_stx(
                        self,
                        arguments_syntax,
                        pre_existing_files_case.value,
                        Arrangement(
                            symbols=src_dir_symbol.symbol_table,
                            tcds=TcdsArrangement(
                                tcds_contents=src_dir_relativity.populator_for_relativity_option_root__s(
                                    src_dir_contents_case.value
                                )
                            )
                        ),
                        Expectation(
                            ParseExpectation(
                                source=asrt_source.is_at_end_of_line(1),
                                symbol_references=src_dir_symbol.references_assertion,
                            ),
                            execution=ExecutionExpectation(
                                main_result=asrt_files.DirContainsExactly.of_elements(
                                    list(pre_existing_files_case.value) +
                                    list(src_dir_contents_case.value)
                                )
                            )
                        ),
                    )


def validation_exe_cases(source_dir_name: str,
                         dst_path_symbol_name: str,
                         ) -> Sequence[NExArr[PrimAndExeExpectation[FilesSource, pathlib.Path],
                                              Arrangement]]:
    return [
        NExArr(
            'dir_partition={}, invalid_contents={}'.format(
                dir_partition_case.name,
                invalid_contents_case.name),
            PrimAndExeExpectation.of_exe(
                validation=dir_partition_case.expectation
            ),
            Arrangement(
                symbols=dir_partition_case.arrangement.symbols.in_arrangement(),
                tcds=TcdsArrangement(
                    tcds_contents=dir_partition_case.arrangement.populator_for_relativity_option_root__s(
                        invalid_contents_case.value
                    )
                )
            )
        )
        for dir_partition_case in dir_partition_cases_for_validation(dst_path_symbol_name)
        for invalid_contents_case in invalid_contents_cases(source_dir_name)
    ]


def invalid_contents_cases(source_dir_name: str) -> Sequence[NameAndValue[FileSystemElements]]:
    return [
        NameAndValue(
            'source do not exist',
            (),
        ),
        NameAndValue(
            'source is a regular file',
            [fs.File.empty(source_dir_name)],
        ),
    ]


def dir_partition_cases_for_validation(dst_path_symbol_name: str,
                                       ) -> Sequence[NArrEx[RelativityOptionConfiguration, ValidationAssertions]]:
    return [
        NArrEx(
            DirectoryStructurePartition.HDS.name,
            _relativity_conf_for_symbol(dst_path_symbol_name, RelOptionType.REL_HDS_CASE),
            ValidationAssertions.pre_sds_fails__w_any_msg(),
        ),
        NArrEx(
            DirectoryStructurePartition.NON_HDS.name,
            _relativity_conf_for_symbol(dst_path_symbol_name, RelOptionType.REL_ACT),
            ValidationAssertions.post_sds_fails__w_any_msg(),
        ),
    ]


def _relativity_conf_for_symbol(symbol_name: str,
                                actual_relativity: RelOptionType,
                                ) -> RelativityOptionConfiguration:
    return relativity_options.symbol_conf_rel_any(actual_relativity,
                                                  symbol_name,
                                                  RELATIVITY_VARIANTS__READ__BEFORE_ACT)


def is_src_dir_argument(symbol_name: str) -> Assertion[SymbolReference]:
    return path_references.is_reference_to__path_or_string(
        symbol_name,
        RELATIVITY_VARIANTS__READ__BEFORE_ACT
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
