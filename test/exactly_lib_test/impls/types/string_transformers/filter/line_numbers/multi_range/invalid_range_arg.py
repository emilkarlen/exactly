import unittest

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, \
    ParseExpectation, ExecutionExpectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.test_resources.validation import pre_sds_validation_fails__w_any_msg


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEveryRangeShouldBeValidated(),
    ])


class TestEveryRangeShouldBeValidated(unittest.TestCase):
    def runTest(self):
        invalid_int_expr = args.SingleLineRange('1.5')
        valid_int_expr = args.SingleLineRange('1')
        range_expression_cases = [
            [invalid_int_expr, valid_int_expr, valid_int_expr],
            [valid_int_expr, invalid_int_expr, valid_int_expr],
            [valid_int_expr, valid_int_expr, invalid_int_expr],
        ]
        for range_expressions in range_expression_cases:
            with self.subTest([str(r) for r in range_expressions]):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    args.filter_line_nums__multi(range_expressions).as_remaining_source,
                    model_constructor.arbitrary(self),
                    arrangement_wo_tcds(),
                    Expectation(
                        ParseExpectation(
                        ),
                        ExecutionExpectation(
                            validation=pre_sds_validation_fails__w_any_msg(),
                        ),
                    )
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
