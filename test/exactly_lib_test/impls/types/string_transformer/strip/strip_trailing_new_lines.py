import unittest
from typing import List

from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.strip.test_resources import \
    no_leading_or_trailing_space_cases, only_leading_space_cases, trailing_new_lines_cases_w_leading_space
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax as args
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformer.test_resources import may_dep_on_ext_resources
from exactly_lib_test.impls.types.string_transformer.test_resources.integration_check import \
    expectation_of_successful_execution_2
from exactly_lib_test.test_resources.test_utils import ArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestNoLeadingOrTrailingSpace(),
        TestOnlyLeadingSpace(),
        TestTrailingNewLinesWLeadingSpace(),
        TestDoNotStripTrailingNonNewLineSpace(),
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [args.strip_trailing_new_lines()]


class TestNoLeadingOrTrailingSpace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in no_leading_or_trailing_space_cases():
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check(
                    self,
                    case.value,
                    case.value,
                )


class TestOnlyLeadingSpace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in only_leading_space_cases():
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check(
                    self,
                    case.value,
                    case.value,
                )


class TestTrailingNewLinesWLeadingSpace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in trailing_new_lines_cases_w_leading_space():
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check(self,
                       case.input_value,
                       case.expected_value)


class TestDoNotStripTrailingNonNewLineSpace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            ArrEx(['\n', '\n', ' '],
                  ['\n', '\n', ' '],
                  ),
            ArrEx(['1\n', '\n', ' '],
                  ['1\n', '\n', ' '],
                  ),
            ArrEx(['\n', '2\n', ' '],
                  ['\n', '2\n', ' '],
                  ),
            ArrEx(['\n', '\n', ' \n'],
                  ['\n', '\n', ' '],
                  ),
            ArrEx(['1\n', '\n', ' \n'],
                  ['1\n', '\n', ' '],
                  ),
            ArrEx(['\n', '2\n', ' \n'],
                  ['\n', '2\n', ' '],
                  ),
        ]
        # ACT & ASSERT #
        for case in cases:
            with self.subTest(repr(case.arrangement)):
                # ACT & ASSERT #
                _check(self,
                       case.arrangement,
                       case.expectation)


def _check(put: unittest.TestCase,
           input_lines: List[str],
           expected_lines: List[str],
           ):
    integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
        put,
        Arguments(args.strip_trailing_new_lines()),
        model_constructor.of_lines(put, input_lines),
        arrangement_w_tcds(),
        expectation_of_successful_execution_2(
            symbol_references=asrt.is_empty_sequence,
            output_lines=expected_lines,
            may_depend_on_external_resources=False,
            is_identity_transformer=False,
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
