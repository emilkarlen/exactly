import unittest
from typing import Sequence

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolUsage
from exactly_lib.test_case.result import svh
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation2, ParseExpectation, \
    ExecutionExpectation, SourceArrangement
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh, svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.w_depth_limits.case_generator import \
    SingleCaseGenerator, ExecutionResult, FullExecutionResult, RecWLimArguments, ModelFile, ValidationFailure, \
    MultipleExecutionCasesGenerator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_resources.arguments_building import SequenceOfArguments, ArgumentElementsRenderer, \
    OptionArgument
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

PARSER = sut.parser.Parser()

INSTRUCTION_CHECKER = instruction_check.Checker(
    PARSER
)
RECURSION_OPTION_ARG = OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name)
RECURSION_OPTION_STR = str(RECURSION_OPTION_ARG)


def execute_single(put: unittest.TestCase,
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
            tcds=TcdsArrangementPostAct.of_tcds(case.tcds_arrangement()),
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


def execute_list(put: unittest.TestCase,
                 cases: Sequence[NameAndValue[SingleCaseGenerator]]):
    for case in cases:
        with put.subTest(case.name):
            execute_single(put, case.value)


def execute_multi(put: unittest.TestCase,
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
                    tcds=TcdsArrangementPostAct.of_tcds(case.arrangement.tcds),
                    symbols=case.arrangement.symbols,
                ),
            )
            for case in generator.execution_cases()
        ],
    )


def _symbol_usages_assertion(reference_assertions: Sequence[ValueAssertion[SymbolReference]]
                             ) -> ValueAssertion[Sequence[SymbolUsage]]:
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
               generic_arguments: RecWLimArguments) -> ArgumentElementsRenderer:
    return SequenceOfArguments([
        RelOptPathArgument(model_file.name,
                           model_file.location,
                           ),
        fm_args.DirContentsRecursiveArgs(
            generic_arguments.files_matcher,
            generic_arguments.min_depth,
            generic_arguments.max_depth
        ),
    ])


def _mk_validation_assertion(passes: bool) -> ValueAssertion[svh.SuccessOrValidationErrorOrHardError]:
    return (
        asrt_svh.is_success()
        if passes
        else
        asrt_svh.is_validation_error()
    )
