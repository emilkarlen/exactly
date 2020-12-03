import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.integer.test_resources.validation_cases import \
    failing_integer_validation_cases, IntegerValidationCase
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, \
    ParseExpectation, ExecutionExpectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.filter.line_numbers.test_resources import \
    IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources import parse_check
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestParseFailsWhenRangeIsMissing(),
        TestValidationPreSdsShouldFailWhenRangeExprHasNotExpectedParts(),
        unittest.makeSuite(TestValidationPreSdsShouldFailWhenIntExprIsNotAnExpressionThatEvaluatesToAnInteger),
    ])


class TestParseFailsWhenRangeIsMissing(unittest.TestCase):
    def runTest(self):
        def mk_arguments(range_expr: str) -> ArgumentElementsRenderer:
            return args.filter_line_nums(args.CustomRange(range_expr))

        parse_check.PARSE_CHECKER__SIMPLE.check_invalid_syntax_cases_for_expected_valid_token(
            self,
            mk_arguments,
        )


class TestValidationPreSdsShouldFailWhenRangeExprHasNotExpectedParts(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue(
                'just space',
                '  ',
            ),
            NameAndValue(
                'just space, w new-line',
                ' \n ',
            ),
            NameAndValue(
                'just a separator',
                '{SEPARATOR}',
            ),
            NameAndValue(
                'just two separators',
                '{SEPARATOR}{SEPARATOR}',
            ),
            NameAndValue(
                'too many separators 1',
                '{SEPARATOR}1{SEPARATOR}',
            ),
            NameAndValue(
                'too many separators 2',
                '1{SEPARATOR}{SEPARATOR}',
            ),
            NameAndValue(
                'too many separators 3',
                '1{SEPARATOR}2{SEPARATOR}',
            ),
        ]
        for case in cases:
            with self.subTest(case.name,
                              expr=case.value):
                range_expr_symbol = StringSymbolContext.of_constant(
                    'RANGE_SYMBOL',
                    case.value,
                    default_restrictions=IS_RANGE_EXPR_STR_REFERENCE_RESTRICTIONS,
                )
                arguments = args.filter_line_nums(args.CustomRange(range_expr_symbol.name__sym_ref_syntax))
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    arguments.as_remaining_source,
                    model_constructor.arbitrary(self),
                    arrangement_wo_tcds(
                        symbols=range_expr_symbol.symbol_table,
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=range_expr_symbol.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=validation.pre_sds_validation_fails__w_any_msg(),
                        ),
                    )
                )


class TestValidationPreSdsShouldFailWhenIntExprIsNotAnExpressionThatEvaluatesToAnInteger(unittest.TestCase):
    def test__single_int(self):
        for case in failing_integer_validation_cases():
            range_cases = [
                args.SingleLineRange(case.integer_expr_string),
                args.UpperLimitRange(case.integer_expr_string),
                args.LowerLimitRange(case.integer_expr_string),
            ]
            for range_case in range_cases:
                with self.subTest(invalid_value=case.case_name,
                                  range_case=range_case):
                    self._check(case, range_case)

    def test__lower_and_upper_limit__invalid_lower(self):
        for case in failing_integer_validation_cases():
            range_arg = args.LowerAndUpperLimitRange(case.integer_expr_string,
                                                     '1')
            with self.subTest(invalid_value=case.case_name):
                self._check(case, range_arg)

    def test__lower_and_upper_limit__invalid_upper(self):
        for case in failing_integer_validation_cases():
            range_arg = args.LowerAndUpperLimitRange('1',
                                                     case.integer_expr_string)
            with self.subTest(invalid_value=case.case_name):
                self._check(case, range_arg)

    def _check(self, case: IntegerValidationCase, range_arg: args.Range):
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            args.filter_line_nums(range_arg).as_remaining_source,
            model_constructor.arbitrary(self),
            arrangement_wo_tcds(
                symbols=case.symbol_table,
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=case.symbol_references_expectation,
                ),
                ExecutionExpectation(
                    validation=case.assertions,
                ),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
