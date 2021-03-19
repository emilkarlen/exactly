import itertools
import unittest
from typing import Sequence, Optional, List

from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.condition import comparators
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.test_resources.validation import validation
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.case_generator import \
    SingleCaseGenerator, ExecutionResult, RESULT__MATCHES, RecWLimArguments, ValidationFailure, \
    MultipleExecutionCasesGenerator, FullExecutionResult
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.files_matcher_integration import \
    NumFilesSetup
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.helper_utils import DepthArgs, \
    LimitationCase
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.impls.types.files_matcher.models.test_resources import model_checker
from exactly_lib_test.impls.types.files_matcher.models.test_resources import test_data
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.impls.types.integer.test_resources.validation_cases import \
    failing_integer_validation_cases
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, Dir, File
from exactly_lib_test.test_resources.test_utils import NEA, NExArr
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_data_rest
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringIntConstantSymbolContext


class SymbolReferencesShouldBeReported(SingleCaseGenerator):
    the_checked_dir_contents = test_data.FILE_SYS__WITH_4_LEVELS

    min_depth = NameAndValue('min_depth_symbol', 1)
    max_depth = NameAndValue('max_depth_symbol', 2)

    expected_and_actual = test_data.expected_is_actual_within_depth_limits(
        min_depth=min_depth.value,
        max_depth=max_depth.value,
        actual=the_checked_dir_contents,
    )

    def arguments(self) -> FileMatcherArg:
        return _as_arguments(
            RecWLimArguments(
                self._helper.files_matcher_sym_ref_arg(),
                SymbolReferenceArgument(self.min_depth.name),
                SymbolReferenceArgument(self.max_depth.name),
            ))

    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        return self._helper.tcds_arrangement_for_contents_of_checked_dir(
            self.expected_and_actual.actual
        )

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts([
            FilesMatcherSymbolContext.of_sdv(
                self.files_matcher_name,
                model_checker.matcher(
                    put,
                    self.model_file.path,
                    test_data.strip_file_type_info(self.expected_and_actual.expected),
                )
            ),
            StringIntConstantSymbolContext(
                self.min_depth.name,
                self.min_depth.value,
            ),
            StringIntConstantSymbolContext(
                self.max_depth.name,
                self.max_depth.value,
            ),
        ])

    def expected_symbols(self) -> Sequence[Assertion[SymbolReference]]:
        return [
            asrt_sym_ref.matches_reference_2(
                self.min_depth.name,
                asrt_data_rest.equals__w_str_rendering(
                    reference_restrictions.is_string__all_indirect_refs_are_strings())
            ),
            asrt_sym_ref.matches_reference_2(
                self.max_depth.name,
                asrt_data_rest.equals__w_str_rendering(
                    reference_restrictions.is_string__all_indirect_refs_are_strings())
            ),
            self._helper.files_matcher_sym_assertion(),
        ]

    def execution_result(self) -> ExecutionResult:
        return RESULT__MATCHES


def validation_pre_sds_should_fail_when_limits_are_not_expressions_that_evaluates_to_an_integer(
) -> Sequence[NameAndValue[SingleCaseGenerator]]:
    cases = itertools.chain.from_iterable([
        [
            NEA(
                'min/' + int_expr_case.integer_expr_string,
                int_expr_case.reference_assertions,
                (
                    DepthArgs(min_depth=int_expr_case.integer_expr_string),
                    int_expr_case.symbol_table,
                ),
            ),
            NEA(
                'max/' + int_expr_case.integer_expr_string,
                int_expr_case.reference_assertions,
                (
                    DepthArgs(max_depth=int_expr_case.integer_expr_string),
                    int_expr_case.symbol_table,
                ),
            ),
            NEA(
                'min & max/' + int_expr_case.integer_expr_string,
                int_expr_case.reference_assertions * 2,
                (
                    DepthArgs(min_depth=int_expr_case.integer_expr_string,
                              max_depth=int_expr_case.integer_expr_string,
                              ),
                    int_expr_case.symbol_table,
                ),
            ),
        ]
        for int_expr_case in failing_integer_validation_cases()
    ])

    return [
        NameAndValue(
            case.name,
            _ValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnIntegerCase(
                case.actual[0],
                case.actual[1],
                case.expected,
            ))
        for case in cases
    ]


def validation_pre_sds_should_fail_when_limits_are_integer_out_of_range(

) -> Sequence[NameAndValue[SingleCaseGenerator]]:
    out_of_range_int = '-1'
    in_range_int = '0'
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

    return [
        NameAndValue(
            arguments_case.name,
            _ValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(arguments_case.value)
        )
        for arguments_case in arguments_cases
    ]


def files_of_model() -> Sequence[NameAndValue[SingleCaseGenerator]]:
    the_checked_dir_contents = test_data.FILE_SYS__WITH_4_LEVELS

    cases = [
        NameAndValue(
            'min',
            LimitationCase(
                DepthArgs(min_depth=2),
                test_data.expected_is_actual_from_min_depth(
                    min_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
        ),
        NameAndValue(
            'max',
            LimitationCase(
                DepthArgs(max_depth=2),
                test_data.expected_is_actual_down_to_max_depth(
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
        ),
        NameAndValue(
            'min & max',
            LimitationCase(
                DepthArgs(min_depth=1,
                          max_depth=2),
                test_data.expected_is_actual_within_depth_limits(
                    min_depth=1,
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
        ),
        NameAndValue(
            'evaluated min & max',
            LimitationCase(
                DepthArgs(min_depth='0+1',
                          max_depth='3-1'),
                test_data.expected_is_actual_within_depth_limits(
                    min_depth=1,
                    max_depth=2,
                    actual=the_checked_dir_contents,
                ),
            ),
        ),
    ]

    return [
        NameAndValue(
            case.name,
            _TestFilesOfModel(
                the_checked_dir_contents,
                case.value,
            )
        )
        for case in cases
    ]


class SelectorShouldBeApplied(MultipleExecutionCasesGenerator):
    min_depth = 1
    max_depth = 1

    num_regular_files_eq_1 = [
        Dir('lvl0', [
            File.empty('lvl1-included'),
            Dir('lvl1-not-included', [
                File.empty('lvl2-not-included-file'),
                Dir.empty('lvl2-not-included-dir'),
            ])
        ])
    ]
    num_regular_files_eq_2 = [
        Dir('lvl0', [
            File.empty('lvl1-included-1'),
            File.empty('lvl1-included-2'),
            Dir('lvl1-not-included', [
                File.empty('lvl2-not-included-file'),
                Dir.empty('lvl2-not-included-dir'),
            ])
        ])
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

    def arguments(self) -> FileMatcherArg:
        return _as_arguments(
            RecWLimArguments(
                fms_args.Selection(
                    fm_args.Type(FileType.REGULAR),
                    self.num_files_setup.num_files_arg()
                ),
                self.min_depth,
                self.max_depth,
            )
        )

    def expected_symbols(self) -> Sequence[Assertion[SymbolReference]]:
        return ()

    def execution_cases(self) -> Sequence[NExArr[ExecutionResult, Arrangement]]:
        return [
            NExArr(
                num_files_setup.name,
                FullExecutionResult(num_files_setup.expected),
                Arrangement(
                    tcds=self._helper.tcds_arrangement_for_contents_of_checked_dir(
                        num_files_setup.actual
                    )
                )
            )
            for num_files_setup in self.num_files_setup.cases
        ]


class _ValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnIntegerCase(SingleCaseGenerator):
    def __init__(self,
                 depth_args: DepthArgs,
                 symbols: SymbolTable,
                 symbol_references: Sequence[Assertion[SymbolReference]],
                 ):
        super().__init__()
        self._depth_args = depth_args
        self._symbols = symbols
        self._symbol_references = symbol_references

    def arguments(self) -> FileMatcherArg:
        return _as_arguments(
            RecWLimArguments(
                _ARBITRARY_NON_SYMBOL_FILES_MATCHER,
                self._depth_args.min_depth,
                self._depth_args.max_depth,
            )
        )

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return self._symbols

    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        return None

    def expected_symbols(self) -> Sequence[Assertion[SymbolReference]]:
        return self._symbol_references

    def execution_result(self) -> ExecutionResult:
        return ValidationFailure(validation.PRE_SDS_FAILURE_EXPECTATION)


class _ValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(SingleCaseGenerator):
    def __init__(self, depth_args: DepthArgs):
        super().__init__()
        self._depth_args = depth_args

    def arguments(self) -> FileMatcherArg:
        return _as_arguments(
            RecWLimArguments(
                _ARBITRARY_NON_SYMBOL_FILES_MATCHER,
                self._depth_args.min_depth,
                self._depth_args.max_depth,
            )
        )

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return SymbolTable.empty()

    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        return None

    def expected_symbols(self) -> Sequence[Assertion[SymbolReference]]:
        return ()

    def execution_result(self) -> ExecutionResult:
        return ValidationFailure(validation.PRE_SDS_FAILURE_EXPECTATION)


class _TestFilesOfModel(SingleCaseGenerator):
    def __init__(self,
                 checked_dir_contents: List[FileSystemElement],
                 case: LimitationCase,
                 ):
        super().__init__()
        self._checked_dir_contents = checked_dir_contents
        self._case = case

    def arguments(self) -> FileMatcherArg:
        return _as_arguments(
            RecWLimArguments(
                self._helper.files_matcher_sym_ref_arg(),
                self._case.depth_args.min_depth,
                self._case.depth_args.max_depth,
            )
        )

    def symbols(self, put: unittest.TestCase) -> SymbolTable:
        return SymbolTable({
            self.files_matcher_name:
                model_checker.matcher__sym_tbl_container(put,
                                                         self._helper.model_file_path(),
                                                         test_data.strip_file_type_info(self._case.data.expected),
                                                         )
        })

    def tcds_arrangement(self) -> Optional[TcdsArrangement]:
        return self._helper.tcds_arrangement_for_contents_of_checked_dir(
            self._checked_dir_contents,
        )

    def expected_symbols(self) -> Sequence[Assertion[SymbolReference]]:
        return [
            self._helper.files_matcher_sym_assertion(),
        ]

    def execution_result(self) -> ExecutionResult:
        return RESULT__MATCHES


def _as_arguments(args: RecWLimArguments) -> FileMatcherArg:
    return fm_args.DirContentsRecursiveArgs(
        args.files_matcher,
        args.min_depth,
        args.max_depth
    )


_ARBITRARY_NON_SYMBOL_FILES_MATCHER = fms_args.Empty()
