import unittest
from typing import List

from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.impls.types.string_models.test_resources.model_constructor import ModelConstructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_building as args
from exactly_lib_test.impls.types.string_transformers.test_resources import may_dep_on_ext_resources
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):

    def model(self, may_depend_on_external_resources: bool) -> ModelConstructor:
        model_lines = [
            '{}\n'.format(n + 1)
            for n in range(10)
        ]
        return model_constructor.of_lines(self, model_lines, may_depend_on_external_resources)

    def expected_output_lines_for_model(self) -> ValueAssertion[List[str]]:
        return asrt.anything_goes()

    def argument_cases(self) -> List[str]:
        return [
            args.filter_line_nums(args.SingleLineRange('7')).as_str,
            args.filter_line_nums(args.SingleLineRange('-7')).as_str,
            args.filter_line_nums(args.UpperLimitRange('5')).as_str,
            args.filter_line_nums(args.UpperLimitRange('-5')).as_str,
            args.filter_line_nums(args.LowerLimitRange('5')).as_str,
            args.filter_line_nums(args.LowerLimitRange('-5')).as_str,

            args.filter_line_nums(args.LowerAndUpperLimitRange('5', '6')).as_str,
            args.filter_line_nums(args.LowerAndUpperLimitRange('-8', '8')).as_str,
            args.filter_line_nums(args.LowerAndUpperLimitRange('2', '-2')).as_str,
            args.filter_line_nums(args.LowerAndUpperLimitRange('-5', '-3')).as_str,

            args.filter_line_nums__multi([args.SingleLineRange('5'), args.SingleLineRange('6')]).as_str,

            args.filter_line_nums__multi([args.SingleLineRange('-5'), args.SingleLineRange('-6')]).as_str,
        ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
