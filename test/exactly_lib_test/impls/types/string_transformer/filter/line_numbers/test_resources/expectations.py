from typing import List, Sequence, Callable

from exactly_lib.impls.types.string_transformer.impl.filter.line_nums.range_expr import Range, SingleLineRange, \
    LowerLimitRange, UpperLimitRange, LowerAndUpperLimitRange
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, ParseExpectation, \
    ExecutionExpectation, prim_asrt__constant
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources.ranges import \
    ValidRange
from exactly_lib_test.impls.types.string_transformer.test_resources.integration_check import StExpectation
from exactly_lib_test.test_resources.test_utils import InpExp
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.string_.test_resources.reference_assertions import \
    IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer

IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS = IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS

InputAndExpected = InpExp[List[str], List[str]]


class LinesContentsExpectation:
    def __init__(self,
                 lines: List[str],
                 may_depend_on_external_resources: Callable[[bool], bool],
                 ):
        self.lines = lines
        self.may_dep_on_ext_rsrc = may_depend_on_external_resources

    @staticmethod
    def ext_deps_of_source(lines: List[str]) -> 'LinesContentsExpectation':
        return LinesContentsExpectation(
            lines,
            lambda x: x,
        )

    @staticmethod
    def const_expt_deps(lines: List[str],
                        expt_deps: bool) -> 'LinesContentsExpectation':
        return LinesContentsExpectation(
            lines,
            lambda x: expt_deps,
        )

    @staticmethod
    def const_false_expt_deps(lines: List[str]) -> 'LinesContentsExpectation':
        return LinesContentsExpectation.const_expt_deps(
            lines,
            False,
        )

    @staticmethod
    def of_is_const_empty(lines: List[str],
                          is_const_empty: bool) -> 'LinesContentsExpectation':
        return (
            LinesContentsExpectation.const_false_expt_deps(lines)
            if is_const_empty
            else
            LinesContentsExpectation.ext_deps_of_source(lines)
        )


InputAndExpectedWExtDeps = InpExp[List[str], LinesContentsExpectation]


def inp_exp__w_ext_deps(wo_expt_deps: InputAndExpected,
                        the_range: ValidRange) -> InputAndExpectedWExtDeps:
    return InpExp(
        wo_expt_deps.input,
        LinesContentsExpectation.of_is_const_empty(wo_expt_deps.expected,
                                                   the_range.is_const_empty))


def is_single(line_number: int) -> Assertion[Range]:
    return asrt.is_instance_with(
        SingleLineRange,
        asrt.sub_component('line_number',
                           lambda x: x.line_number,
                           asrt.equals(line_number)
                           )
    )


def is_lower(lower_limit: int) -> Assertion[Range]:
    return asrt.is_instance_with(
        LowerLimitRange,
        asrt.sub_component('lower_limit',
                           lambda x: x.lower_limit,
                           asrt.equals(lower_limit)
                           )
    )


def is_upper(upper_limit: int) -> Assertion[Range]:
    return asrt.is_instance_with(
        UpperLimitRange,
        asrt.sub_component('upper_limit',
                           lambda x: x.upper_limit,
                           asrt.equals(upper_limit)
                           )
    )


def is_lower_and_upper(lower_limit: int,
                       upper_limit: int) -> Assertion[Range]:
    return asrt.is_instance_with__many(
        LowerAndUpperLimitRange,
        [
            asrt.sub_component('lower_limit',
                               lambda x: x.lower_limit,
                               asrt.equals(lower_limit)
                               ),
            asrt.sub_component('upper_limit',
                               lambda x: x.upper_limit,
                               asrt.equals(upper_limit)
                               ),
        ]
    )


def expectation_of_successful_execution__check_only_as_lines(
        output_lines: List[str],
        symbol_references: Assertion[Sequence[SymbolReference]],
        source: Assertion[ParseSource] = asrt.anything_goes(),
) -> StExpectation:
    return Expectation(
        ParseExpectation(
            source=source,
            symbol_references=symbol_references
        ),
        ExecutionExpectation(
            main_result=asrt_string_source.matches__lines__check_just_as_lines(output_lines),
        ),
        prim_asrt__constant(
            asrt_string_transformer.is_identity_transformer(False)
        )
    )
