"""
Test cases

* Positive number

 1      n (n+1)
|*--*---*|*---
| actual |
"""
import itertools
import unittest
from typing import List

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.multi_range.test_resources import Case
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.multi_range.test_resources import \
    CheckerOfConstInput
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources import \
    IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources.argument_building import Range
from exactly_lib_test.impls.types.string_transformers.test_resources.argument_building import to_, from_, from_to, \
    single
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import ArrEx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringIntConstantSymbolContext, \
    StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestModelWNumLines0),
        unittest.makeSuite(TestModelWNumLines1),
        unittest.makeSuite(TestModelWNumLines10),
        TestSymbolReferences(),
        TestIntIsPyExprAndSourceConsumption(),
    ])


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = ['1\n', '2\n', '3\n']
        single_range_1_symbol = StringIntConstantSymbolContext(
            'RANGE_SYMBOL_1',
            -1,
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        single_range_2_symbol = StringIntConstantSymbolContext(
            'RANGE_SYMBOL_2',
            -3,
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        symbols = [single_range_1_symbol, single_range_2_symbol]

        expected_output_lines = [input_lines[0],
                                 input_lines[2]]

        arguments = args.filter_line_nums__multi([
            args.SingleLineRange(single_range_1_symbol.name__sym_ref_syntax),
            args.SingleLineRange(single_range_2_symbol.name__sym_ref_syntax),
        ])
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            integration_check.expectation_of_successful_execution_2(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


class TestIntIsPyExprAndSourceConsumption(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = ['1\n', '2\n', '3\n']
        single_range_1_symbol = StringConstantSymbolContext(
            'RANGE_SYMBOL_1',
            '-1+10-10',
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        single_range_2_symbol = StringConstantSymbolContext(
            'RANGE_SYMBOL_2',
            '7-10:7-10',
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        symbols = [single_range_1_symbol, single_range_2_symbol]

        expected_output_lines = [input_lines[1 - 1],
                                 input_lines[3 - 1]]

        arguments = args.filter_line_nums__multi([
            args.SingleLineRange(single_range_1_symbol.name__sym_ref_syntax),
            args.SingleLineRange(single_range_2_symbol.name__sym_ref_syntax),
        ])
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            integration_check.expectation_of_successful_execution_2(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


class TestModelWNumLines0(unittest.TestCase):
    INPUT = []
    RANGES_CASES = [
        [to_(-2), to_(3)],
        [to_(-2), to_(-3)],
        [to_(-2), from_(2)],
        [to_(-2), from_(-2)],
        [to_(-3), from_to(2, -2)],
        [from_(-3), from_to(2, -2)],
        [from_(3), from_to(-4, -2)],
        [from_(3), from_to(2, 5)],
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        for ranges in self.RANGES_CASES:
            with self.subTest([str(r) for r in ranges]):
                checker.check__wo_max_lines_from_iter(
                    ranges,
                    [],
                )

    def test_with_model_access__check_all_model_properties(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        for ranges in self.RANGES_CASES:
            with self.subTest([str(r) for r in ranges]):
                checker.check__w_access_of_all_model_properties(
                    ranges,
                    [],
                )


def _combined_line_numbers(ranges: List[List[int]]) -> List[int]:
    all_values = set(itertools.chain.from_iterable(ranges))
    return list(sorted(all_values))


def _case_of(args_and_output_list: List[ArrEx[Range, List[int]]]) -> Case:
    arguments = [
        args_and_output.arrangement
        for args_and_output in args_and_output_list
    ]
    expected_line_numbers = _combined_line_numbers([
        args_and_output.expectation
        for args_and_output in args_and_output_list
    ])
    return Case.w_upper_limit(
        str([str(r) for r in arguments]),
        arguments,
        expected_line_numbers
    )


class TestModelWNumLines1(unittest.TestCase):
    INPUT = ['1\n']

    _SINGLE_NEG__1 = ArrEx(single(-1), [1])
    _SINGLE_NEG__BEFORE = ArrEx(single(-2 - 1), [])

    _TO_NEG__BEFORE = ArrEx(to_(-2), [])
    _TO_NEG__1 = ArrEx(to_(-1), [1])
    _TO_POS__AFTER = ArrEx(to_(2), [1])

    _FROM_NEG__BEFORE = ArrEx(from_(-2), [1])
    _FROM_NEG__1 = ArrEx(from_(-1), [1])
    _FROM_POS__AFTER = ArrEx(from_(2), [])

    _FROM_TO__m1_m1 = ArrEx(from_to(-1, -1), [1])
    _FROM_TO__m2_m1 = ArrEx(from_to(-2, -1), [1])
    _FROM_TO__m1_2 = ArrEx(from_to(-1, 2), [1])

    RANGES_CASES = [
        [_SINGLE_NEG__1, _SINGLE_NEG__BEFORE],

        [_TO_NEG__BEFORE, _TO_NEG__BEFORE],
        [_TO_NEG__BEFORE, _TO_NEG__1],
        [_TO_NEG__BEFORE, _TO_POS__AFTER],

        [_FROM_NEG__BEFORE, _FROM_NEG__BEFORE],
        [_FROM_NEG__BEFORE, _FROM_NEG__1],
        [_FROM_NEG__BEFORE, _FROM_POS__AFTER],

        [_FROM_TO__m1_m1, _FROM_TO__m1_m1],
        [_FROM_TO__m1_m1, _FROM_TO__m1_2],
        [_FROM_TO__m2_m1, _FROM_TO__m1_2],

        [_SINGLE_NEG__1, _FROM_TO__m2_m1],
        [_SINGLE_NEG__1, _FROM_TO__m2_m1],
        [_SINGLE_NEG__BEFORE, _FROM_POS__AFTER],

        [_TO_NEG__BEFORE, _FROM_TO__m1_2, _SINGLE_NEG__1, _FROM_POS__AFTER],
    ]

    CASES = [
        _case_of(case)
        for case in RANGES_CASES
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        checker.check__wo_max_lines_from_iter__cases(self.CASES)

    def test_with_model_access__check_all_model_properties(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        checker.check__w_access_of_all_model_properties__cases(self.CASES)


def _int_list(a: int, b: int) -> List[int]:
    return list(range(a, b + 1))


class TestModelWNumLines10(unittest.TestCase):
    INPUT = [
        '{}\n'.format(n + 1)
        for n in range(10)
    ]

    _SINGLE_NEG__MIDDLE = ArrEx(single(-5), [6])
    _SINGLE_NEG__FIRST = ArrEx(single(-10), [1])

    _TO_NEG = ArrEx(to_(-2), _int_list(1, 9))
    _TO_POS = ArrEx(to_(4), _int_list(1, 4))
    _TO_AFTER_MAX = ArrEx(to_(10 + 1), _int_list(1, 10))

    _FROM_NEG = ArrEx(from_(-3), _int_list(8, 10))
    _FROM_POS = ArrEx(from_(7), _int_list(7, 10))
    _FROM_MAX = ArrEx(from_(10), [10])
    _FROM_AFTER_MAX = ArrEx(from_(10 + 1), [])

    _FROM_TO__2_3 = ArrEx(from_to(2, 3), _int_list(2, 3))
    _FROM_TO_NEG_NEG = ArrEx(from_to(-3, -2), _int_list(8, 9))
    _FROM_TO_NEG_POS = ArrEx(from_to(-9, 3), _int_list(2, 3))
    _FROM_TO_POS_NEG = ArrEx(from_to(7, -4), [7])
    _FROM_TO_POS_POS = ArrEx(from_to(10, 12), [10])

    RANGES_CASES = [
        [_TO_NEG, _TO_POS],
        [_FROM_NEG, _FROM_POS],
        [_FROM_NEG, _TO_AFTER_MAX],
        [_FROM_TO_NEG_NEG, _FROM_TO_POS_NEG],
        [_FROM_TO_POS_POS, _FROM_TO_NEG_POS],
        [_TO_NEG, _FROM_POS, _FROM_TO_NEG_POS, _FROM_TO_NEG_POS, _FROM_TO_POS_POS],
        [_SINGLE_NEG__MIDDLE, _SINGLE_NEG__FIRST],
    ]

    CASES = [
        _case_of(case)
        for case in RANGES_CASES
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        checker.check__wo_max_lines_from_iter__cases(self.CASES)

    def test_with_model_access__check_all_model_properties(self):
        checker = CheckerOfConstInput(
            self,
            self.INPUT,
            max_as_lines_invocations__when_only_checking_via_as_lines=2,
        )
        checker.check__w_access_of_all_model_properties__cases(self.CASES)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
