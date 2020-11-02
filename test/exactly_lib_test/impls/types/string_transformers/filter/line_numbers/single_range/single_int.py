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
from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers import test_resources as tr
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources import InputAndExpected, \
    IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.test_utils import NArrEx, InpExp
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


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
    return args.filter_line_nums(args.SingleLineRange(str(int_expr)))


class TestIntIsPyExprAndSourceConsumption(unittest.TestCase):
    def runTest(self):
        input_lines = ['1st\n', '2nd\n', '3rd\n']
        range_expr = '1+1'
        evaluated_expr = 2
        expected_output_lines = [input_lines[evaluated_expr - 1]]

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
        expected_output_lines = input_lines[0:1]
        range_expr = StringSymbolContext.of_constant(
            'RANGE_SYMBOL',
            '1',
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
            integration_check.expectation_of_successful_execution(
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
            [],
        ),
        NArrEx(
            'in range',
            1,
            INPUT_LINES,
        ),
        NArrEx(
            'too large',
            2,
            [],
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_max_lines_from_iter(
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
            [],
        ),
        NArrEx(
            'in range - 1st',
            1,
            [ACTUAL_1],
        ),
        NArrEx(
            'in range - in middle',
            2,
            [ACTUAL_2],
        ),
        NArrEx(
            'in range - last',
            3,
            [ACTUAL_3],
        ),
        NArrEx(
            'outside range - too large',
            4,
            [],
        ),
    ]

    def test_with_model_access__only_as_lines_is_used(self):
        for case in self.CASES:
            with self.subTest(case.name, range=case.arrangement):
                _check_int_arg__w_max_lines_from_iter(
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
            'too small',
            -2,
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


class TestNegativeIntOnNonModelWMultipleLines(unittest.TestCase):
    actual_1 = '1st\n'
    actual_2 = '2nd\n'
    actual_3 = '3rd\n'
    INPUT_LINES = [actual_1, actual_2, actual_3]
    CASES = [
        NArrEx(
            'in range - last',
            -1,
            [actual_3],
        ),
        NArrEx(
            'in range - in middle',
            -2,
            [actual_2],
        ),
        NArrEx(
            'in range - first',
            -3,
            [actual_1],
        ),
        NArrEx(
            'outside range - too small',
            -4,
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


def _check_int_arg__w_max_lines_from_iter(put: unittest.TestCase,
                                          arg: int,
                                          input_and_expected: InputAndExpected,
                                          ):
    return tr.check__w_max_lines_from_iter(
        put,
        [args.SingleLineRange(str(arg))],
        arg,
        input_and_expected,
    )


def _check_int_arg__wo_max_lines_from_iter(put: unittest.TestCase,
                                           range_expr: int,
                                           input_and_expected: InputAndExpected,
                                           ):
    tr.check__w_max_as_lines_invocations__wo_max_lines_from_iter(
        put,
        [args.SingleLineRange(str(range_expr))],
        input_and_expected
    )


def _check_int_arg__w_access_of_all_model_properties(put: unittest.TestCase,
                                                     range_expr: int,
                                                     input_and_expected: InputAndExpected,
                                                     ):
    tr.check__w_access_of_all_model_properties(
        put,
        [args.SingleLineRange(str(range_expr))],
        input_and_expected,
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
