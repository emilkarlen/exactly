import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_utils.condition.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.files_matcher_integration import \
    NumFilesSetup
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.helper_utils import \
    IntegrationCheckHelper, DepthArgs, LimitationCase
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.model_contents import \
    model_checker
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation, arrangement_wo_tcds, Arrangement
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_resources.arguments_building import OptionArgument
from exactly_lib_test.test_resources.files.file_structure import Dir, empty_file, empty_dir
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestParseShouldFailWhenInvalidLimitOption(),
        TestValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnInteger(),
        TestValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(),
        TestFilesOfModel(),
        TestSymbolReferencesShouldBeReported(),
        TestSelectorShouldBeApplied(),
    ])


class TestParseShouldFailWhenInvalidLimitOption(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            integration_check.CHECKER.parser.parse(
                fm_args.InvalidDirContentsRecursive(
                    OptionArgument(a.OptionName('invalid-option'))
                ).as_remaining_source
            )


class TestValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnInteger(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        helper = IntegrationCheckHelper()
        for int_expr_case in failing_integer_validation_cases():
            arguments_cases = [
                NEA(
                    'min',
                    int_expr_case.reference_assertions,
                    DepthArgs(min_depth=int_expr_case.integer_expr_string),
                ),
                NEA(
                    'max',
                    int_expr_case.reference_assertions,
                    DepthArgs(max_depth=int_expr_case.integer_expr_string),
                ),
                NEA(
                    'min & max',
                    int_expr_case.reference_assertions * 2,
                    DepthArgs(min_depth=int_expr_case.integer_expr_string,
                              max_depth=int_expr_case.integer_expr_string,
                              ),
                ),
            ]
            for arguments_case in arguments_cases:
                with self.subTest(invalid_value=int_expr_case.case_name,
                                  arguments=arguments_case.name):
                    # ACT & ASSERT #
                    integration_check.CHECKER.check(
                        self,
                        source=
                        fm_args.DirContentsRecursive(
                            _ARBITRARY_NON_SYMBOL_FILES_MATCHER,
                            min_depth=arguments_case.actual.min_depth,
                            max_depth=arguments_case.actual.max_depth,
                        ).as_remaining_source,
                        model_constructor=helper.model_constructor_for_checked_dir(),
                        arrangement=
                        Arrangement(
                            symbols=int_expr_case.symbol_table,
                        ),
                        expectation=
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.matches_sequence(arguments_case.expected),
                            ),
                            ExecutionExpectation(
                                validation=int_expr_case.expectation,
                            ),
                        )
                    )


class TestValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        out_of_range_int = '-1'
        in_range_int = '0'
        helper = IntegrationCheckHelper()
        arguments_cases = [
            NameAndValue(
                'min',
                DepthArgs(min_depth=out_of_range_int),
            ),
            NameAndValue(
                'max',
                DepthArgs(max_depth=out_of_range_int),
            ),
            NameAndValue(
                'min & max - min out of range',
                DepthArgs(min_depth=out_of_range_int,
                          max_depth=in_range_int,
                          ),
            ),
            NameAndValue(
                'min & max - max out of range',
                DepthArgs(min_depth=in_range_int,
                          max_depth=out_of_range_int,
                          ),
            ),
        ]
        for arguments_case in arguments_cases:
            with self.subTest(invalid_value=arguments_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check(
                    self,
                    source=
                    fm_args.DirContentsRecursive(
                        _ARBITRARY_NON_SYMBOL_FILES_MATCHER,
                        min_depth=arguments_case.value.min_depth,
                        max_depth=arguments_case.value.max_depth,
                    ).as_remaining_source,
                    model_constructor=helper.model_constructor_for_checked_dir(),
                    arrangement=
                    arrangement_wo_tcds(),
                    expectation=
                    Expectation(
                        ParseExpectation(),
                        ExecutionExpectation(
                            validation=validation.pre_sds_validation_fails__w_any_msg(),
                        ),
                    )
                )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        the_checked_dir_contents = test_data.FILE_SYS__WITH_4_LEVELS

        cases = [
            LimitationCase(
                'min',
                DepthArgs(min_depth=2),
                test_data.expected_is_actual_from_min_depth(
                    min_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
            LimitationCase(
                'max',
                DepthArgs(max_depth=2),
                test_data.expected_is_actual_down_to_max_depth(
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
            LimitationCase(
                'min & max',
                DepthArgs(min_depth=1,
                          max_depth=2),
                test_data.expected_is_actual_within_depth_limits(
                    min_depth=1,
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
            LimitationCase(
                'evaluated min & max',
                DepthArgs(min_depth='0+1',
                          max_depth='3-1'),
                test_data.expected_is_actual_within_depth_limits(
                    min_depth=1,
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
        ]

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        for case in cases:
            with self.subTest(case.name):
                integration_check.CHECKER.check_single_multi_execution_setup(
                    self,
                    arguments=fm_args.DirContentsRecursive(
                        helper.files_matcher_sym_ref_arg(),
                        min_depth=case.depth_args.min_depth,
                        max_depth=case.depth_args.max_depth,
                    ).as_arguments,
                    parse_expectation=
                    helper.parse_expectation_of_symbol_references(),
                    model_constructor=
                    helper.model_constructor_for_checked_dir(),
                    execution=NExArr(
                        case.name,
                        ExecutionExpectation(),
                        helper.arrangement_for_contents_of_model(
                            checked_dir_contents=the_checked_dir_contents,
                            files_matcher_symbol_value=
                            model_checker.matcher(self,
                                                  helper.checked_dir_path(),
                                                  test_data.strip_file_type_info(case.data.expected),
                                                  ),
                        ),
                    ),
                )


class TestSymbolReferencesShouldBeReported(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        the_checked_dir_contents = test_data.FILE_SYS__WITH_4_LEVELS

        min_depth = NameAndValue('min_depth_symbol', 1)
        max_depth = NameAndValue('max_depth_symbol', 2)

        expected_and_actual = test_data.expected_is_actual_within_depth_limits(
            min_depth=min_depth.value,
            max_depth=max_depth.value,
            actual=the_checked_dir_contents,
        )

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        integration_check.CHECKER.check(
            self,
            source=fm_args.DirContentsRecursive(
                helper.files_matcher_sym_ref_arg(),
                min_depth=SymbolReferenceArgument(min_depth.name),
                max_depth=SymbolReferenceArgument(max_depth.name),
            ).as_remaining_source,
            model_constructor=
            helper.model_constructor_for_checked_dir(),
            arrangement=
            Arrangement(
                tcds=helper.tcds_arrangement_for_contents_of_model(expected_and_actual.actual),
                symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                    helper.files_matcher_name:
                        model_checker.matcher(self,
                                              helper.checked_dir_path(),
                                              test_data.strip_file_type_info(expected_and_actual.expected),
                                              ),
                    min_depth.name:
                        symbol_utils.string_sdvs.str_constant(str(min_depth.value)),
                    max_depth.name:
                        symbol_utils.string_sdvs.str_constant(str(max_depth.value)),
                })
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_sequence([
                        equals_symbol_reference(SymbolReference(min_depth.name,
                                                                string_made_up_by_just_strings())),
                        equals_symbol_reference(SymbolReference(max_depth.name,
                                                                string_made_up_by_just_strings())),
                        is_reference_to_files_matcher__ref(helper.files_matcher_name),
                    ])
                ),
            )
        )


class TestSelectorShouldBeApplied(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        min_depth = 1
        max_depth = 1

        num_regular_files_eq_1 = [
            Dir('lvl0', [
                empty_file('lvl1-included'),
                Dir('lvl1-not-included', [
                    empty_file('lvl2-not-included-file'),
                    empty_dir('lvl2-not-included-dir'),
                ])
            ]
                )
        ]
        num_regular_files_eq_2 = [
            Dir('lvl0', [
                empty_file('lvl1-included-1'),
                empty_file('lvl1-included-2'),
                Dir('lvl1-not-included', [
                    empty_file('lvl2-not-included-file'),
                    empty_dir('lvl2-not-included-dir'),
                ])
            ]
                )
        ]
        num_files_setup = NumFilesSetup(
            comparators.EQ,
            2,
            [
                NEA('not match',
                    False,
                    num_regular_files_eq_1,
                    ),
                NEA('match',
                    True,
                    num_regular_files_eq_2,
                    ),
            ]
        )

        helper = IntegrationCheckHelper()

        # ACT & ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            arguments=fm_args.DirContentsRecursive(
                fms_args.Selection(
                    fm_args.Type(FileType.REGULAR),
                    num_files_setup.num_files_arg()
                ),
                min_depth=min_depth,
                max_depth=max_depth,
            ).as_arguments,
            parse_expectation=
            ParseExpectation(),
            model_constructor=
            helper.model_constructor_for_checked_dir(),
            execution=[
                NExArr(
                    num_files_setup.name,
                    ExecutionExpectation(
                        main_result=asrt_matching_result.matches_value(num_files_setup.expected)
                    ),
                    Arrangement(
                        tcds=helper.tcds_arrangement_for_contents_of_model(
                            num_files_setup.actual
                        )
                    )
                )
                for num_files_setup in num_files_setup.cases
            ]
            ,
        )


_ARBITRARY_NON_SYMBOL_FILES_MATCHER = fms_args.Empty()
