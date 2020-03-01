import unittest
from pathlib import PurePosixPath
from typing import Mapping, Optional

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.symbol_syntax import SymbolWithReferenceSyntax
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources.string import is_string_made_up_of_just_strings_reference_to__ref
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrEx
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_condition.test_resources import primitive_assertions as asrt_primitive
from exactly_lib_test.test_case_utils.files_condition.test_resources.integration_check import CHECKER
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_wo_tcds, Expectation, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_case_utils.test_resources.validation import pre_sds_validation_fails__w_any_msg
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidFileNamesShouldCauseValidationError),
        unittest.makeSuite(TestFileNamesShouldUsePosixSyntax),
        unittest.makeSuite(TestEachUniqueFileNameShouldHaveAnEntryInFilesMapping),
    ])


class Case:
    def __init__(self,
                 name: str,
                 source: args.FilesCondition,
                 symbols: SymbolsArrEx,
                 ):
        self.name = name
        self.source = source
        self.symbols = symbols


class CaseWithFiles:
    def __init__(self,
                 name: str,
                 source: args.FilesCondition,
                 symbols: SymbolsArrEx,
                 expected: Mapping[PurePosixPath, ValueAssertion[Optional[FileMatcher]]]
                 ):
        self.name = name
        self.source = source
        self.symbols = symbols
        self.expected = expected


class TestInvalidFileNamesShouldCauseValidationError(unittest.TestCase):
    def test_files_names_must_be_relative(self):
        # ARRANGE #
        cases = [
            Case(
                'absolute posix file name (constant)',
                args.FilesCondition([
                    args.FileCondition(ABS_POSIX_PATH),
                ]),
                SymbolsArrEx.empty(),
            ),
            Case(
                'valid file name and absolute posix file name (constant)',
                args.FilesCondition([
                    args.FileCondition('valid-file-name'),
                    args.FileCondition(ABS_POSIX_PATH),
                ]),
                SymbolsArrEx.empty(),
            ),
            Case(
                'absolute posix file name (symbol ref)',
                args.FilesCondition([
                    args.FileCondition(SymbolWithReferenceSyntax(ABS_POSIX_PATH_SYMBOL_NAME)),
                ]),
                SymbolsArrEx(
                    {
                        ABS_POSIX_PATH_SYMBOL_NAME:
                            string_sdvs.str_constant(ABS_POSIX_PATH)
                    },
                    [is_string_made_up_of_just_strings_reference_to__ref(ABS_POSIX_PATH_SYMBOL_NAME)]
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                CHECKER.check__w_source_variants(
                    self,
                    case.source.as_arguments,
                    None,
                    arrangement_wo_tcds(case.symbols.symbol_table),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.symbols.expected_references_assertion
                        ),
                        ExecutionExpectation(
                            validation=pre_sds_validation_fails__w_any_msg()
                        )
                    )
                )


class TestFileNamesShouldUsePosixSyntax(unittest.TestCase):
    def test_forward_slash_should_separate_parts(self):
        # ARRANGE #
        multi_part_file_name = '/'.join(FILE_NAME_PARTS)
        expected_file_names = {
            PurePosixPath(*FILE_NAME_PARTS): asrt.is_none
        }

        multi_part_file_name_symbol = NameAndValue(
            'multi_part_file_name_symbol',
            string_sdvs.str_constant(multi_part_file_name)
        )

        cases = [
            Case(
                'multi part posix file name (constant)',
                args.FilesCondition([
                    args.FileCondition(multi_part_file_name),
                ]),
                SymbolsArrEx.empty(),
            ),
            Case(
                'multi part posix file name (symbol reference)',
                args.FilesCondition([
                    args.FileCondition(SymbolWithReferenceSyntax(multi_part_file_name_symbol.name)),
                ]),
                SymbolsArrEx.of_navs(
                    [multi_part_file_name_symbol],
                    [is_string_made_up_of_just_strings_reference_to__ref(multi_part_file_name_symbol.name)]
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                CHECKER.check__w_source_variants(
                    self,
                    case.source.as_arguments,
                    None,
                    arrangement_wo_tcds(case.symbols.symbol_table),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.symbols.expected_references_assertion
                        ),
                        ExecutionExpectation(
                            main_result=asrt.is_none,
                        ),
                        primitive=asrt_primitive.files_matches(expected_file_names)
                    )
                )

    def test_back_slash_should_not_separate_parts(self):
        # ARRANGE #
        file_name_with_back_slash = '\\'.join(FILE_NAME_PARTS)
        expected_file_names = {
            PurePosixPath(file_name_with_back_slash): asrt.is_none
        }
        source = args.FilesCondition([
            args.FileCondition(surrounded_by_hard_quotes(file_name_with_back_slash)),
        ])

        # ACT & ASSERT #
        CHECKER.check__w_source_variants(
            self,
            source.as_arguments,
            None,
            arrangement_wo_tcds(),
            Expectation(
                ParseExpectation(),
                ExecutionExpectation(),
                primitive=asrt_primitive.files_matches(expected_file_names)
            )
        )


class TestEachUniqueFileNameShouldHaveAnEntryInFilesMapping(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            CaseWithFiles(
                'single file name',
                args.FilesCondition([
                    args.FileCondition('file-name'),
                ]),
                SymbolsArrEx.empty(),
                {PurePosixPath('file-name'): asrt.is_none}
            ),
            CaseWithFiles(
                'two file names',
                args.FilesCondition([
                    args.FileCondition('fn1'),
                    args.FileCondition('fn2'),
                ]),
                SymbolsArrEx.empty(),
                {
                    PurePosixPath('fn1'): asrt.is_none,
                    PurePosixPath('fn2'): asrt.is_none,
                }
            ),
            CaseWithFiles(
                'two files with the same names',
                args.FilesCondition([
                    args.FileCondition('fn'),
                    args.FileCondition('fn'),
                ]),
                SymbolsArrEx.empty(),
                {
                    PurePosixPath('fn'): asrt.is_none,
                }
            ),
            CaseWithFiles(
                'some unique files, some repeated',
                args.FilesCondition([
                    args.FileCondition('fn1'),
                    args.FileCondition('fn2'),
                    args.FileCondition('fn1'),
                ]),
                SymbolsArrEx.empty(),
                {
                    PurePosixPath('fn1'): asrt.is_none,
                    PurePosixPath('fn2'): asrt.is_none,
                }
            ),
            CaseWithFiles(
                'different symbols with identical value',
                args.FilesCondition([
                    args.FileCondition(SymbolWithReferenceSyntax('sym_ref1')),
                    args.FileCondition(SymbolWithReferenceSyntax('sym_ref2')),
                ]),
                SymbolsArrEx(
                    {
                        'sym_ref1': string_sdvs.str_constant('fn'),
                        'sym_ref2': string_sdvs.str_constant('fn'),
                    },
                    [
                        is_string_made_up_of_just_strings_reference_to__ref('sym_ref1'),
                        is_string_made_up_of_just_strings_reference_to__ref('sym_ref2'),
                    ]
                ),
                {
                    PurePosixPath('fn'): asrt.is_none,
                }
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                CHECKER.check__w_source_variants(
                    self,
                    case.source.as_arguments,
                    None,
                    arrangement_wo_tcds(case.symbols.symbol_table),
                    Expectation(
                        ParseExpectation(
                            symbol_references=case.symbols.expected_references_assertion
                        ),
                        ExecutionExpectation(),
                        asrt_primitive.files_matches(case.expected)
                    )
                )


ABS_POSIX_PATH = '/absolute/path'
ABS_POSIX_PATH_SYMBOL_NAME = 'abs_posix_path_symbol_name'
FILE_NAME_PARTS = ['fst', 'snd']