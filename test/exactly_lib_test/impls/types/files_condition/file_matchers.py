import unittest
from pathlib import PurePosixPath
from typing import Optional, Mapping, Sequence

from exactly_lib.type_val_prims.files_condition import FilesCondition
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.name_and_value import NameAndValue, NavBuilder
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as args
from exactly_lib_test.impls.types.files_condition.test_resources import primitive_assertions as asrt_primitive
from exactly_lib_test.impls.types.files_condition.test_resources.complex_matcher_checking import \
    ApplicationSequenceFrom1Builder, matches_w_application_order
from exactly_lib_test.impls.types.files_condition.test_resources.integration_check import CHECKER
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_wo_tcds, \
    ParseExpectation, ExecutionExpectation, PrimAndExeExpectation, Expectation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import prim_asrt__constant
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import NExArr, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.symbol_context import FileMatcherSymbolContext, \
    FileMatcherSymbolContextOfPrimitiveConstant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidationErrorShouldBeDetected),
        unittest.makeSuite(TestApplicationWithMax1MatcherPerFile),
        unittest.makeSuite(TestMultipleMatchersForFileShouldBeCombinedWithConjunctionInOrderOfAppearance),
    ])


class TestValidationErrorShouldBeDetected(unittest.TestCase):
    def test_validation_error_SHOULD_be_reported_WHEN_file_matcher_reports_validation_error(self):
        # ARRANGE #
        fm_symbol_name = 'the_file_matcher'
        arguments = args.FilesCondition([
            args.FileCondition('file-name',
                               fm_args.SymbolReferenceWReferenceSyntax(fm_symbol_name))
        ])
        # ACT & ASSERT #
        CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_file_matcher(fm_symbol_name)
            ),
            input_=None,
            execution=validation_cases.failing_validation_cases__multi_exe(fm_symbol_name)
        )

    def test_validation_error_SHOULD_be_reported_WHEN_file_name_is_invalid(self):
        # ARRANGE #
        valid_fm = FileMatcherSymbolContext.of_primitive_constant('a_valid_file_matcher', True)
        arguments = args.FilesCondition([
            args.FileCondition('/an/absolute/file/name',
                               fm_args.SymbolReferenceWReferenceSyntax(valid_fm.name)),
        ])
        # ACT & ASSERT #
        CHECKER.check(
            self,
            arguments.as_remaining_source,
            None,
            arrangement_wo_tcds(
                valid_fm.symbol_table
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        valid_fm.reference_assertion
                    )
                ),
                ExecutionExpectation(
                    validation=ValidationAssertions.pre_sds_fails__w_any_msg()
                )
            )
        )


class TestApplicationWithMax1MatcherPerFile(unittest.TestCase):
    def test_single_file_name_with_matcher(self):
        # ARRANGE #
        file_name = 'file-name'
        fm_symbol = 'file_matcher'
        cases = [
            NameAndValue(
                'single name entry',
                args.FilesCondition([
                    args.FileCondition(file_name,
                                       fm_args.SymbolReferenceWReferenceSyntax(fm_symbol))
                ]),
            ),
            NameAndValue(
                'two entries with same file name, 1st without and 2nd with FileMatcher',
                args.FilesCondition([
                    args.FileCondition(file_name),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm_symbol)),
                ]),
            ),
            NameAndValue(
                'two entries with same file name, 1st with and 2nd without FileMatcher',
                args.FilesCondition([
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm_symbol)),
                    args.FileCondition(file_name),
                ]),
            ),
        ]
        # ACT & ASSERT #
        for case in cases:
            with self.subTest(case.name):
                CHECKER.check_multi__w_source_variants(
                    self,
                    case.value.as_arguments,
                    asrt.matches_sequence([
                        is_reference_to_file_matcher(fm_symbol)
                    ]),
                    None,
                    [
                        NExArr(
                            'FileMatcher should give {}'.format(expected_result),
                            PrimAndExeExpectation.of_prim__const(
                                asrt_primitive.files_matches({
                                    PurePosixPath(file_name):
                                        asrt_primitive.is_matcher_that_gives(expected_result)
                                })
                            ),
                            arrangement_wo_tcds(
                                FileMatcherSymbolContext.of_primitive_constant(
                                    fm_symbol,
                                    expected_result).symbol_table
                            ),
                        )
                        for expected_result in [False, True]
                    ]
                )

    def test_one_file_wo_matcher_and_one_w_matcher(self):
        # ARRANGE #
        file_name_w_matcher = 'file-name-with-matcher'
        file_name_wo_matcher = 'file-name-without-matcher'

        fm_symbol = 'file_matcher'

        arguments = args.FilesCondition([
            args.FileCondition(file_name_wo_matcher),
            args.FileCondition(file_name_w_matcher, fm_args.SymbolReferenceWReferenceSyntax(fm_symbol)),
        ])
        # ACT & ASSERT #
        CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            asrt.matches_sequence([
                is_reference_to_file_matcher(fm_symbol)
            ]),
            None,
            [
                NExArr(
                    'FileMatcher should give {}'.format(expected_result),
                    PrimAndExeExpectation.of_prim__const(
                        asrt_primitive.files_matches({
                            PurePosixPath(file_name_wo_matcher):
                                asrt.is_none,
                            PurePosixPath(file_name_w_matcher):
                                asrt_primitive.is_matcher_that_gives(expected_result)
                        })
                    ),
                    arrangement_wo_tcds(
                        FileMatcherSymbolContext.of_primitive_constant(
                            fm_symbol,
                            expected_result).symbol_table
                    ),
                )
                for expected_result in [False, True]
            ]
        )

    def test_two_different_files_w_matcher(self):
        # ARRANGE #
        file_name__constant = 'file-name-with-constant-matcher'
        file_name__w_variations = 'file-name-with-matcher-with-variations'

        fm__constant = FileMatcherSymbolContextOfPrimitiveConstant('fm_constant', True)
        fm__w_variations = 'fm_w_variations'

        arguments = args.FilesCondition([
            args.FileCondition(file_name__constant, fm_args.SymbolReferenceWReferenceSyntax(fm__constant.name)),
            args.FileCondition(file_name__w_variations, fm_args.SymbolReferenceWReferenceSyntax(fm__w_variations)),
        ])
        # ACT & ASSERT #
        CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            asrt.matches_sequence([
                fm__constant.reference_assertion,
                is_reference_to_file_matcher(fm__w_variations),
            ]),
            None,
            [
                NExArr(
                    'FileMatcher with variations should give {}'.format(expected_result_of_matcher_w_variations),
                    PrimAndExeExpectation.of_prim__const(
                        asrt_primitive.files_matches({

                            PurePosixPath(file_name__constant):
                                asrt_primitive.is_matcher_that_gives(fm__constant.result_value),

                            PurePosixPath(file_name__w_variations):
                                asrt_primitive.is_matcher_that_gives(expected_result_of_matcher_w_variations)
                        })
                    ),
                    arrangement_wo_tcds(
                        SymbolContext.symbol_table_of_contexts([
                            fm__constant,
                            FileMatcherSymbolContext.of_primitive_constant(fm__w_variations,
                                                                           expected_result_of_matcher_w_variations),
                        ])
                    ),
                )
                for expected_result_of_matcher_w_variations in [False, True]
            ]
        )

    def test_file_matcher_SHOULD_be_parsed_as_full_expression(self):
        # ARRANGE #
        file_name = 'file-name'
        fm_1 = FileMatcherSymbolContextOfPrimitiveConstant('file_matcher_1', False)
        fm_2 = FileMatcherSymbolContextOfPrimitiveConstant('file_matcher_2', True)
        symbols = [fm_1, fm_2]

        arguments = args.FilesCondition([
            args.FileCondition(file_name,
                               fm_args.disjunction([fm_1.argument,
                                                    fm_2.argument]))
        ])
        expected_result = fm_1.result_value or fm_2.result_value
        # ACT & ASSERT #
        CHECKER.check__w_source_variants(
            self,
            arguments=arguments.as_arguments,
            input_=None,
            arrangement=arrangement_wo_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols)
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbols)
                ),
                primitive=
                prim_asrt__constant(
                    asrt_primitive.files_matches({
                        PurePosixPath(file_name):
                            asrt_primitive.is_matcher_that_gives(expected_result)
                    })
                )
            )
        )


class TestMultipleMatchersForFileShouldBeCombinedWithConjunctionInOrderOfAppearance(unittest.TestCase):
    def test_single_repeated_file_name__2_w_fm_1_wo_fm(self):
        # ARRANGE #
        file_name = 'file-name'
        fm1_symbol = NavBuilder('fm1')
        fm2_symbol = NavBuilder('fm2')
        cases = [
            NameAndValue(
                'two entries',
                args.FilesCondition([
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm1_symbol.name)),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm2_symbol.name)),
                ]),
            ),
            NameAndValue(
                'one empty entry above',
                args.FilesCondition([
                    args.FileCondition(file_name),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm1_symbol.name)),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm2_symbol.name)),
                ]),
            ),
            NameAndValue(
                'one empty entry between',
                args.FilesCondition([
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm1_symbol.name)),
                    args.FileCondition(file_name),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm2_symbol.name)),
                ]),
            ),
            NameAndValue(
                'one empty entry below',
                args.FilesCondition([
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm1_symbol.name)),
                    args.FileCondition(file_name, fm_args.SymbolReferenceWReferenceSyntax(fm2_symbol.name)),
                    args.FileCondition(file_name),
                ]),
            ),
        ]
        # ACT & ASSERT #
        for case in cases:
            with self.subTest(case.name):
                CHECKER.check_multi(
                    self,
                    case.value.as_arguments,
                    ParseExpectation(
                        symbol_references=asrt.matches_sequence([
                            is_reference_to_file_matcher(fm1_symbol.name),
                            is_reference_to_file_matcher(fm2_symbol.name),
                        ])
                    ),
                    None,
                    [
                        result_is_single_file_name_w_lazy_conjunction_w_1st_is_applied_before_2nd(
                            file_name,
                            fm1_symbol.build(fm1),
                            fm2_symbol.build(fm2),
                        )
                        for (fm1, fm2) in [(False, False),
                                           (False, True),
                                           (True, False),
                                           (True, True)]
                    ]
                )

    def test_3_file_names__1_fn_2_times_w_matchers_that_should_be_combined(self):
        # ARRANGE #
        fn_1_time_wo_fm = 'file-name--1-time--wo-matcher'
        fn_1_time_w_fm = 'file-name-1-time--w-matcher'
        fn_2_times_w_fm = 'file-name-2-times--w-matcher'

        fn_1_time__fm = NavBuilder('fn_1_time__fm')
        fn_2_times__fm_1 = NavBuilder('fn_2_times__fm_1')
        fn_2_times__fm_2 = NavBuilder('fn_2_times__fm_2')

        cases = [
            NIE(
                'files wo matcher combination : before',
                [
                    is_reference_to_file_matcher(fn_1_time__fm.name),
                    is_reference_to_file_matcher(fn_2_times__fm_1.name),
                    is_reference_to_file_matcher(fn_2_times__fm_2.name),

                ],
                args.FilesCondition([
                    args.FileCondition(fn_1_time_wo_fm),
                    args.FileCondition(fn_1_time_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_1_time__fm.name)),
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_1.name)),
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_2.name)),
                ]),
            ),
            NIE(
                'files wo matcher combination : between',
                [
                    is_reference_to_file_matcher(fn_2_times__fm_1.name),
                    is_reference_to_file_matcher(fn_1_time__fm.name),
                    is_reference_to_file_matcher(fn_2_times__fm_2.name),
                ],
                args.FilesCondition([
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_1.name)),
                    args.FileCondition(fn_1_time_wo_fm),
                    args.FileCondition(fn_1_time_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_1_time__fm.name)),
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_2.name)),
                ]),
            ),
            NIE(
                'files wo matcher combination : after',
                [
                    is_reference_to_file_matcher(fn_2_times__fm_1.name),
                    is_reference_to_file_matcher(fn_2_times__fm_2.name),
                    is_reference_to_file_matcher(fn_1_time__fm.name),
                ],
                args.FilesCondition([
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_1.name)),
                    args.FileCondition(fn_2_times_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_2_times__fm_2.name)),
                    args.FileCondition(fn_1_time_wo_fm),
                    args.FileCondition(fn_1_time_w_fm, fm_args.SymbolReferenceWReferenceSyntax(fn_1_time__fm.name)),
                ]),
            ),
        ]
        # ACT & ASSERT #
        for case in cases:
            with self.subTest(case.name):
                CHECKER.check_multi(
                    self,
                    case.input_value.as_arguments,
                    ParseExpectation(
                        symbol_references=asrt.matches_sequence(case.expected_value)
                    ),
                    None,
                    [
                        result_is_single_file_name_w_lazy_conjunction_w_1st_is_applied_before_2nd(
                            fn_2_times_w_fm,
                            fn_2_times__fm_1.build(fm1),
                            fn_2_times__fm_2.build(fm2),
                            additional_symbols=[
                                FileMatcherSymbolContext.of_primitive_constant(fn_1_time__fm.name, fm2)
                            ],
                            additional_entries={
                                PurePosixPath(fn_1_time_wo_fm): asrt.is_none,
                                PurePosixPath(fn_1_time_w_fm): asrt_primitive.is_matcher_that_gives(fm2),
                            }
                        )
                        for (fm1, fm2) in [(False, False),
                                           (False, True),
                                           (True, False),
                                           (True, True)]
                    ]
                )


def result_is_single_file_name_w_lazy_conjunction_w_1st_is_applied_before_2nd(
        file_name: str,
        fm1: NameAndValue[bool],
        fm2: NameAndValue[bool],
        additional_symbols: Sequence[SymbolContext] = (),
        additional_entries: Optional[Mapping[PurePosixPath, Assertion[Optional[FileMatcher]]]] = None
) -> NExArr[PrimAndExeExpectation[FilesCondition,
                                  Optional[MatchingResult]],
            Arrangement]:
    expected_result_of_complex = fm1.value and fm2.value

    sequence_builder = ApplicationSequenceFrom1Builder()

    fst_matcher = sequence_builder.add_applied(fm1, 1)
    snd_matcher__w_respect_to_laziness = (
        sequence_builder.add_applied(fm2, 2)
        if fm1.value
        else
        sequence_builder.add_un_applied(fm2)
    )

    symbols = []
    symbols += additional_symbols
    symbols += [
        FileMatcherSymbolContext.of_sdv(fm1.name, fst_matcher),
        FileMatcherSymbolContext.of_sdv(fm2.name, snd_matcher__w_respect_to_laziness),
    ]

    entries = (
        {}
        if additional_entries is None
        else
        dict(additional_entries)
    )
    entries.update({
        PurePosixPath(file_name):
            asrt_primitive.is_matcher_that_gives(expected_result_of_complex)
    })

    return NExArr(
        'combination of {} && {}'.format(fm1.value, fm2.value),
        PrimAndExeExpectation.of_prim__const(
            matches_w_application_order(
                entries,
                sequence_builder.expected_application_sequence()
            )
        ),
        arrangement_wo_tcds(
            SymbolContext.symbol_table_of_contexts(symbols)
        ),
    )
