import unittest
from typing import Sequence, Optional

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.impls.instructions.assert_ import contents_of_dir as sut
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.test_case.result import svh
from exactly_lib.util.functional import reduce_optional
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.contents_of_dir.test_resources import argument_building as args
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation2, \
    ExecutionExpectation, SourceArrangement
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.case_executor import \
    ExecutorOfCaseGenerator
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.case_generator import \
    SingleCaseGenerator, ExecutionResult, FullExecutionResult, ModelFile, ValidationFailure, \
    MultipleExecutionCasesGenerator
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct, \
    TcdsArrangement
from exactly_lib_test.tcfs.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh, svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer, \
    OptionArgument
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion

PARSER = sut.parser.Parser()

INSTRUCTION_CHECKER = instruction_check.Checker(
    PARSER
)
RECURSION_OPTION_ARG = OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name)


class ExecutorOfCaseGeneratorForDirContents(ExecutorOfCaseGenerator):
    def execute_single(self,
                       put: unittest.TestCase,
                       case: SingleCaseGenerator,
                       ):
        INSTRUCTION_CHECKER.check_2(
            put,
            source=_arguments(
                case.model_file,
                case.arguments(),
            ).as_remaining_source,
            arrangement=
            ArrangementPostAct2(
                tcds=_mk_tcds_arrangement_post_act(case.tcds_arrangement()),
                symbols=case.symbols(put),
            ),
            expectation=
            Expectation2(
                ParseExpectation(
                    symbol_usages=_symbol_usages_assertion(case.expected_symbols())
                ),
                _execution_expectation_of(case.execution_result())
            )
        )

    def execute_list(self,
                     put: unittest.TestCase,
                     cases: Sequence[NameAndValue[SingleCaseGenerator]]):
        for case in cases:
            with put.subTest(case.name):
                self.execute_single(put, case.value)

    def execute_multi(self,
                      put: unittest.TestCase,
                      generator: MultipleExecutionCasesGenerator):
        INSTRUCTION_CHECKER.check_multi(
            put,
            source=
            SourceArrangement.new_w_arbitrary_fs_location(
                _arguments(generator.model_file,
                           generator.arguments()).as_arguments
            ),
            parse_expectation=ParseExpectation(
                symbol_usages=_symbol_usages_assertion(generator.expected_symbols())
            ),
            execution=[
                NExArr(
                    case.name,
                    _execution_expectation_of(case.expected),
                    ArrangementPostAct2(
                        tcds=_mk_tcds_arrangement_post_act(case.arrangement.tcds),
                        symbols=case.arrangement.symbols,
                    ),
                )
                for case in generator.execution_cases()
            ],
        )


def _mk_tcds_arrangement_post_act(tcds: Optional[TcdsArrangement]) -> TcdsArrangementPostAct:
    return reduce_optional(TcdsArrangementPostAct.of_tcds,
                           _NEUTRAL_TCDS_POST_ACT,
                           tcds)


_NEUTRAL_TCDS_POST_ACT = TcdsArrangementPostAct()


def _symbol_usages_assertion(reference_assertions: Sequence[Assertion[SymbolReference]]
                             ) -> Assertion[Sequence[SymbolUsage]]:
    return asrt.matches_sequence([
        asrt.is_instance_with(SymbolReference, sr)
        for sr in reference_assertions
    ])


def _execution_expectation_of(expected: ExecutionResult) -> ExecutionExpectation:
    if isinstance(expected, FullExecutionResult):
        return ExecutionExpectation(
            main_result=asrt_pfh.is_non_hard_error(expected.is_match)
        )
    elif isinstance(expected, ValidationFailure):
        return ExecutionExpectation(
            validation_pre_sds=_mk_validation_assertion(expected.expectation.passes_pre_sds),
            validation_post_sds=_mk_validation_assertion(expected.expectation.passes_post_sds),
        )
    raise ValueError(
        'Unknown {}: {}'.format(
            str(type(ExecutionResult)),
            expected,
        )
    )


def _arguments(model_file: ModelFile,
               file_matcher: FileMatcherArg) -> ArgumentElementsRenderer:
    return args.of_file_matcher(
        RelOptPathArgument(model_file.name,
                           model_file.location,
                           ),
        file_matcher,
    )


def _mk_validation_assertion(passes: bool) -> Assertion[svh.SuccessOrValidationErrorOrHardError]:
    return (
        asrt_svh.is_success()
        if passes
        else
        asrt_svh.is_validation_error()
    )
