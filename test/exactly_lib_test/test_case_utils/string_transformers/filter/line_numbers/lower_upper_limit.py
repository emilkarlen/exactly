"""
Test cases

* Positive number

 1      n (n+1)
|*--*---*|*---
| actual |

* Negative number

-(n+1) -n      -1
-----*|*----*---*|
      | actual   |
"""
import unittest
from typing import List

from exactly_lib_test.symbol.test_resources.string import StringSymbolContext, \
    IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers import test_resources as tr
from exactly_lib_test.test_case_utils.string_transformers.filter.line_numbers.test_resources import InputAndExpected
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import InpExp, ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        TestSymbolReferences(),

        unittest.makeSuite(TestEmptyModel),

        unittest.makeSuite(TestLowerPositiveUpperPositiveOnNonModelWSingleLineWHardCodedExpected),
        TestModelWSingleLineAndArbitraryLimits(),
        unittest.makeSuite(TestModelWMultipleLines),

        TestIntIsPyExprAndSourceConsumption(),
    ])


def single_line_arguments(lower_expr: WithToString, upper_expr: WithToString) -> ArgumentElementsRenderer:
    return args.filter_line_nums(args.LowerAndUpperLimitRange(str(lower_expr),
                                                              str(upper_expr)))


class Limits:
    def __init__(self,
                 lower: int,
                 upper: int,
                 ):
        self.lower = lower
        self.upper = upper

    def __str__(self) -> str:
        return 'lower {}, upper {}'.format(self.lower, self.upper)


class TestIntIsPyExprAndSourceConsumption(unittest.TestCase):
    def runTest(self):
        input_lines = ['1st\n', '2nd\n', '3rd\n']
        lower_expr = '1+1'
        upper_expr = '1+2'
        expected_output_lines = input_lines[2 - 1:3]

        arguments = single_line_arguments(lower_expr, upper_expr)
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(
                self,
                input_lines,
                may_depend_on_external_resources=False
            ),
            arrangement_w_tcds(),
            integration_check.expectation_of_successful_execution(
                symbol_references=asrt.is_empty_sequence,
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = ['1\n', '2\n', '3\n']
        expected_output_lines = input_lines[0:2]

        range_lim_l = StringSymbolContext.of_constant(
            'LIMIT__LOWER',
            '1',
            default_restrictions=IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION,
        )
        range_lim_u = StringSymbolContext.of_constant(
            'LIMIT__UPPER',
            '2',
            default_restrictions=IS_STRING_MADE_UP_OF_JUST_STRINGS_REFERENCE_RESTRICTION,
        )
        symbols = [range_lim_l, range_lim_u]

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            single_line_arguments(
                range_lim_l.name__sym_ref_syntax,
                range_lim_u.name__sym_ref_syntax,
            ).as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            integration_check.expectation_of_successful_execution(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            ),
        )


class TestEmptyModel(unittest.TestCase):
    LIMIT_CASES = [-2, -1, 0, 1, 2]
    INPUT_AND_EXPECTED = InpExp([], [])

    def test_with_model_access__only_as_lines_is_used(self):
        for limit__lower in self.LIMIT_CASES:
            for limit__upper in self.LIMIT_CASES:
                limits = Limits(limit__lower, limit__upper)
                with self.subTest(limits=str(limits)):
                    _check_int_arg__wo_max_lines_from_iter(
                        self,
                        limits,
                        self.INPUT_AND_EXPECTED,
                    )

    def test_with_model_access__check_all_model_properties(self):
        for limit__lower in self.LIMIT_CASES:
            for limit__upper in self.LIMIT_CASES:
                limits = Limits(limit__lower, limit__upper)
                with self.subTest(limits=str(limits)):
                    _check_int_arg__w_access_of_all_model_properties(
                        self,
                        limits,
                        self.INPUT_AND_EXPECTED,
                    )


class TestLowerPositiveUpperPositiveOnNonModelWSingleLineWHardCodedExpected(unittest.TestCase):
    INPUT_LINES = ['the one and only line']
    CASES = [
        # lower == 0
        ArrEx(
            Limits(0, 0),
            [],
        ),
        ArrEx(
            Limits(0, 1),
            INPUT_LINES,
        ),
        ArrEx(
            Limits(0, 2),
            INPUT_LINES,
        ),
        ArrEx(
            Limits(0, 3),
            INPUT_LINES,
        ),

        # lower == 1
        ArrEx(
            Limits(1, 0),
            [],
        ),
        ArrEx(
            Limits(1, 1),
            INPUT_LINES,
        ),
        ArrEx(
            Limits(1, 2),
            INPUT_LINES,
        ),
        ArrEx(
            Limits(1, 3),
            INPUT_LINES,
        ),

        # lower == 2
        ArrEx(
            Limits(2, 0),
            [],
        ),
        ArrEx(
            Limits(2, 1),
            [],
        ),
        ArrEx(
            Limits(2, 2),
            [],
        ),
        ArrEx(
            Limits(2, 3),
            [],
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(limits=str(case.arrangement)):
                _check_int_arg__w_max_lines_from_iter(
                    self,
                    case.arrangement,
                    case.arrangement.upper,
                    InpExp(self.INPUT_LINES, case.expectation),
                )

    def test_with_model_access__check_all_model_properties(self):
        for case in self.CASES:
            with self.subTest(limits=str(case.arrangement)):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )


class TestModelWSingleLineAndArbitraryLimits(unittest.TestCase):
    INPUT_LINES = ['the one and only line']

    LIMITS = list(range(-3, 3 + 1))

    def runTest(self):
        for lower in self.LIMITS:
            for upper in self.LIMITS:
                limits = Limits(lower, upper)
                py_limits = _py_non_neg_limits(limits, self.INPUT_LINES)
                expected = self.INPUT_LINES[py_limits.lower:py_limits.upper]
                with self.subTest(limits=str(limits),
                                  expected=expected):
                    _check_int_arg__w_access_of_all_model_properties(
                        self,
                        limits,
                        InpExp(self.INPUT_LINES, expected),
                    )


class TestModelWMultipleLines(unittest.TestCase):
    INPUT_LINES = ['1st\n', '2nd\n', '3rd\n', '4th\n']

    LIMITS = list(range(-6, 6 + 1))
    NON_NEG_LIMITS = list(range(6 + 1))

    def test_with_model_access__only_as_lines_is_used(self):
        for lower in self.LIMITS:
            for upper in self.LIMITS:
                limits = Limits(lower, upper)
                py_limits = _py_non_neg_limits(limits, self.INPUT_LINES)
                expected = self.INPUT_LINES[py_limits.lower:py_limits.upper]
                with self.subTest(limits=str(limits),
                                  expected=expected):
                    _check_int_arg__wo_max_lines_from_iter(
                        self,
                        limits,
                        InpExp(self.INPUT_LINES, expected),
                    )

    def test_with_model_access__non_neg_limits__only_as_lines_is_used_w_max_lines_accessed(self):
        for lower in self.NON_NEG_LIMITS:
            for upper in self.NON_NEG_LIMITS:
                limits = Limits(lower, upper)
                py_limits = _py_non_neg_limits(limits, self.INPUT_LINES)
                expected = self.INPUT_LINES[py_limits.lower:py_limits.upper]
                with self.subTest(limits=str(limits),
                                  expected=expected):
                    _check_int_arg__w_max_lines_from_iter(
                        self,
                        limits,
                        limits.upper,
                        InpExp(self.INPUT_LINES, expected),
                    )

    def test_with_model_access__check_all_model_properties(self):
        for lower in self.LIMITS:
            for upper in self.LIMITS:
                limits = Limits(lower, upper)
                py_limits = _py_non_neg_limits(limits, self.INPUT_LINES)
                expected = self.INPUT_LINES[py_limits.lower:py_limits.upper]
                with self.subTest(limits=str(limits),
                                  expected=expected):
                    _check_int_arg__w_access_of_all_model_properties(
                        self,
                        limits,
                        InpExp(self.INPUT_LINES, expected),
                    )


def _py_non_neg_limits(xly_limits: Limits, actual: List[str]) -> Limits:
    len_of_actual = len(actual)

    lower = xly_limits.lower
    if lower > 0:
        lower -= 1
    elif lower < 0:
        lower = len_of_actual + lower

    upper = xly_limits.upper
    if upper < 0:
        upper = len_of_actual + upper + 1

    if lower < 0:
        lower = 0

    if upper < 0:
        upper = 0

    return Limits(lower, upper)


def _check_int_arg__w_max_lines_from_iter(put: unittest.TestCase,
                                          limits: Limits,
                                          max_lines_accessed: int,
                                          input_and_expected: InputAndExpected,
                                          ):
    return tr.check_int_arg__w_max_lines_from_iter(
        put,
        args.LowerAndUpperLimitRange(str(limits.lower),
                                     str(limits.upper)),
        max_lines_accessed,
        input_and_expected,
    )


def _check_int_arg__wo_max_lines_from_iter(put: unittest.TestCase,
                                           limits: Limits,
                                           input_and_expected: InputAndExpected,
                                           ):
    tr.check_int_arg__wo_max_lines_from_iter(
        put,
        args.LowerAndUpperLimitRange(str(limits.lower),
                                     str(limits.upper)),
        input_and_expected
    )


def _check_int_arg__w_access_of_all_model_properties(put: unittest.TestCase,
                                                     limits: Limits,
                                                     input_and_expected: InputAndExpected,
                                                     ):
    tr.check_int_arg__w_access_of_all_model_properties(
        put,
        args.LowerAndUpperLimitRange(str(limits.lower),
                                     str(limits.upper)),
        input_and_expected,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
