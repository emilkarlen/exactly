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

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources import \
    argument_building as range_args
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources import \
    integration_check as _integration_check
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources import ranges
from exactly_lib_test.impls.types.string_transformer.filter.line_numbers.test_resources.expectations import \
    InputAndExpected, \
    IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS, inp_exp__w_ext_deps
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import NArrEx, InpExp
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        TestSymbolReferences(),

        unittest.makeSuite(TestEmptyModel),

        unittest.makeSuite(TestPositiveIntOnNonModelWSingleLine),
        unittest.makeSuite(TestPositiveIntOnNonModelWMultipleLines),

        unittest.makeSuite(TestNegativeIntOnNonModelWSingleLine),
        unittest.makeSuite(TestNegativeIntOnNonModelWMultipleLines),

        TestIntIsPyExprAndSourceConsumption(),
    ])


def single_line_arguments(int_expr: WithToString) -> ArgumentElementsRenderer:
    return args.filter_line_nums(range_args.LowerLimitRange(str(int_expr)))


class TestIntIsPyExprAndSourceConsumption(unittest.TestCase):
    def runTest(self):
        input_lines = ['1st\n', '2nd\n', '3rd\n']
        range_expr = '1+1'
        evaluated_expr = 2
        expected_output_lines = input_lines[evaluated_expr - 1:]

        arguments = single_line_arguments(range_expr)
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            arguments.as_arguments,
            model_constructor.of_lines(
                self,
                input_lines,
                may_depend_on_external_resources=False
            ),
            arrangement_w_tcds(),
            integration_check.expectation_of_successful_execution_2(
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
        expected_output_lines = input_lines[1:]
        range_expr = StringSymbolContext.of_constant(
            'RANGE_SYMBOL',
            '2',
            default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
        )
        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants_for_full_line_parser_2(
            self,
            single_line_arguments(range_expr.name__sym_ref_syntax).as_arguments,
            model_constructor.of_lines(self, input_lines,
                                       may_depend_on_external_resources=False),
            arrangement_w_tcds(
                symbols=range_expr.symbol_table,
            ),
            integration_check.expectation_of_successful_execution_2(
                symbol_references=range_expr.references_assertion,
                output_lines=expected_output_lines,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
            )
        )


class TestEmptyModel(unittest.TestCase):
    RANGE_CASES = [0, 1, 2, -1, -2]
    INPUT_AND_EXPECTED = InpExp([], [])

    def test_with_model_access__only_as_lines_is_used(self):
        for range_int in self.RANGE_CASES:
            with self.subTest(range_int=range_int):
                _check_int_arg__wo_max_lines_from_iter(
                    self,
                    range_int,
                    self.INPUT_AND_EXPECTED,
                )

    def test_with_model_access__check_all_model_properties(self):
        for range_int in self.RANGE_CASES:
            with self.subTest(range_int=range_int):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    range_int,
                    self.INPUT_AND_EXPECTED,
                )


class TestPositiveIntOnNonModelWSingleLine(unittest.TestCase):
    INPUT_LINES = ['the one and only line']
    CASES = [
        NArrEx(
            '0',
            0,
            INPUT_LINES,
        ),
        NArrEx(
            'in range',
            1,
            INPUT_LINES,
        ),
        NArrEx(
            'above actual num lines',
            2,
            [],
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__wo_max_lines_from_iter(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )

    def test_with_model_access__check_all_model_properties(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )


class TestPositiveIntOnNonModelWMultipleLines(unittest.TestCase):
    ACTUAL_1 = '1st\n'
    ACTUAL_2 = '2nd\n'
    ACTUAL_3 = '3rd\n'
    INPUT_LINES = [ACTUAL_1, ACTUAL_2, ACTUAL_3]
    CASES = [
        NArrEx(
            'outside range - too small',
            0,
            INPUT_LINES,
        ),
        NArrEx(
            'in range - 1st',
            1,
            INPUT_LINES[1 - 1:],
        ),
        NArrEx(
            'in range - in middle',
            2,
            INPUT_LINES[2 - 1:],
        ),
        NArrEx(
            'in range - last',
            3,
            INPUT_LINES[3 - 1:],
        ),
        NArrEx(
            'above actual num lines',
            4,
            [],
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__wo_max_lines_from_iter(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )

    def test_with_model_access__check_all_model_properties(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )


class TestNegativeIntOnNonModelWSingleLine(unittest.TestCase):
    INPUT_LINES = ['the one and only line']
    CASES = [
        NArrEx(
            'in range',
            -1,
            INPUT_LINES,
        ),
        NArrEx(
            'before first line',
            -2,
            INPUT_LINES,
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__wo_max_lines_from_iter(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )

    def test_with_model_access__check_all_model_properties(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )


class TestNegativeIntOnNonModelWMultipleLines(unittest.TestCase):
    actual_1 = '1st\n'
    actual_2 = '2nd\n'
    actual_3 = '3rd\n'
    INPUT_LINES = [actual_1, actual_2, actual_3]
    CASES = [
        NArrEx(
            'in range - last',
            -1,
            INPUT_LINES[3 - 1:],
        ),
        NArrEx(
            'in range - in middle',
            -2,
            INPUT_LINES[3 - 2:],
        ),
        NArrEx(
            'in range - first',
            -3,
            INPUT_LINES[3 - 3:],
        ),
        NArrEx(
            'outside range - before first line',
            -4,
            INPUT_LINES,
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__wo_max_lines_from_iter(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )

    def test_with_model_access__check_all_model_properties(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_access_of_all_model_properties(
                    self,
                    case.arrangement,
                    InpExp(self.INPUT_LINES, case.expectation),
                )


def _check_int_arg__wo_max_lines_from_iter(put: unittest.TestCase,
                                           range_expr: int,
                                           input_and_expected: InputAndExpected,
                                           ):
    _integration_check.check__w_max_as_lines_invocations__wo_max_lines_from_iter(
        put,
        [ranges.from_(range_expr).as_arg],
        input_and_expected
    )


def _check_int_arg__w_access_of_all_model_properties(put: unittest.TestCase,
                                                     range_expr: int,
                                                     inp_exp: InputAndExpected,
                                                     ):
    the_range = ranges.from_(range_expr)
    _integration_check.check__w_access_of_all_model_properties(
        put,
        [the_range.as_arg],
        inp_exp__w_ext_deps(inp_exp, the_range),
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
