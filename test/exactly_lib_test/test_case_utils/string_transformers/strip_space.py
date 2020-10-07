import unittest
from typing import List

from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_case_utils.string_transformers.test_resources.strip_space import \
    no_leading_or_trailing_space_cases
from exactly_lib_test.test_resources.test_utils import ArrEx, NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestNoLeadingOrTrailingSpace(),
        TestOnlyLeadingSpace(),
        TestTrailingNewLinesWLeadingSpace(),
        TestTrailingSpace(),
    ])


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
        cases = [
            NArrEx(
                'single empty line',
                ['\n', 'end'],
                ['end'],
            ),
            NArrEx(
                'single line with space',
                ['  \n', 'end'],
                ['end'],
            ),
            NArrEx(
                'single line with space (tab)',
                ['\t\n', 'end'],
                ['end'],
            ),
            NArrEx(
                'multiple empty lines',
                ['\n', '\n', '\n', 'end'],
                ['end'],
            ),
            NArrEx(
                'leading just-space lines and just-space lines in the middle',
                ['\n', '  \n', 'middle\n', '\n', ' \n', 'end'],
                ['middle\n', '\n', ' \n', 'end'],
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check(
                    self,
                    case.arrangement,
                    case.expectation,
                )


class TestTrailingNewLinesWLeadingSpace(unittest.TestCase):
    def runTest(self):
        cases = [
            NArrEx(
                'single line (non-empty) ended by new-line',
                ['last\n'],
                ['last'],
            ),
            NArrEx(
                'single line (empty) ended by new-line',
                ['\n'],
                [],
            ),
            NArrEx(
                'non-empty and empty line',
                ['1\n', '\n'],
                ['1'],
            ),
            NArrEx(
                'multiple lines - first non-empty',
                ['1\n', '\n', '\n'],
                ['1'],
            ),
            NArrEx(
                'multiple lines - every line empty',
                ['\n', '\n', '\n'],
                [],
            ),
            NArrEx(
                'multiple lines - empty sequence before non-empty contents - ended by new-line',
                ['\n', '\n', 'non-empty\n'],
                ['non-empty'],
            ),
            NArrEx(
                'multiple lines - empty sequence before non-empty contents - ended sequence of empty lines',
                ['\n', '\n', 'non-empty\n', '\n', '\n'],
                ['non-empty'],
            ),
            NArrEx(
                'multiple lines - empty before and after, non-empty-line has space around',
                ['\n', '\n', '  non-empty  \n', '\n', '\n'],
                ['non-empty'],
            ),
        ]

        # ARRANGE #
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                _check(self,
                       case.arrangement,
                       case.expectation)


class TestTrailingSpace(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            ArrEx(['1\n', '  2  \n'],
                  ['1\n', '  2'],
                  ),
            ArrEx(['1\n', '  2  \n', '  '],
                  ['1\n', '  2'],
                  ),
            ArrEx(['\n', '\n', ' '],
                  [],
                  ),
            ArrEx(['1\n', '\n', ' '],
                  ['1'],
                  ),
            ArrEx(['\n', '2\n', ' '],
                  ['2'],
                  ),
            ArrEx(['\n', '\n', ' \n'],
                  [],
                  ),
            ArrEx(['1\n', '\n', ' \n'],
                  ['1'],
                  ),
            ArrEx(['1\n', '\n', ' \n', '2\n', ' 3  \n', '\n', '\n'],
                  ['1\n', '\n', ' \n', '2\n', ' 3'],
                  ),
            ArrEx(['\n', '2\n', ' \n'],
                  ['2'],
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
        Arguments(args.strip_space()),
        model_constructor.of_lines(put, input_lines),
        arrangement_w_tcds(),
        expectation_of_successful_execution(
            symbol_references=asrt.is_empty_sequence,
            output_lines=expected_lines,
            is_identity_transformer=False,
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
