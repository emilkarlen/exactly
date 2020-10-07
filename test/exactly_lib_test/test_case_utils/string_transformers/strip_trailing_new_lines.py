import unittest

from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStripTrailingNewLines()
    ])


class TestStripTrailingNewLines(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NIE('no lines',
                input_value=[],
                expected_value=[],
                ),
            NIE('single line not ended by new-line',
                input_value=['not new-line'],
                expected_value=['not new-line'],
                ),
            NIE('single line (non-empty) ended by new-line',
                input_value=['last\n'],
                expected_value=['last'],
                ),
            NIE('single line (empty) ended by new-line',
                input_value=['\n'],
                expected_value=[],
                ),

            NIE('multiple lines - first non-empty',
                input_value=['1\n', '\n', '\n'],
                expected_value=['1'],
                ),
            NIE('multiple lines - every line empty',
                input_value=['\n', '\n', '\n'],
                expected_value=[],
                ),

            NIE('multiple lines - empty sequence before non-empty contents (preceded by non-empty lines)'
                ' - not ended by new-line',
                input_value=['non-empty\n', '\n', '\n', 'non-empty'],
                expected_value=['non-empty\n', '\n', '\n', 'non-empty'],
                ),
            NIE('multiple lines - empty sequence before non-empty contents - not ended by new-line',
                input_value=['\n', '\n', 'non-empty'],
                expected_value=['\n', '\n', 'non-empty'],
                ),
            NIE('multiple lines - empty sequence before non-empty contents - not ended by new-line (space)',
                input_value=['\n', '\n', ' '],
                expected_value=['\n', '\n', ' '],
                ),
            NIE('multiple lines - empty sequence before non-empty contents - ended by new-line',
                input_value=['\n', '\n', 'non-empty\n'],
                expected_value=['\n', '\n', 'non-empty'],
                ),
            NIE('multiple lines - empty sequence before non-empty contents - ended by new-line (space)',
                input_value=['\n', '\n', ' \n'],
                expected_value=['\n', '\n', ' '],
                ),
            NIE('multiple lines - empty sequence before non-empty contents - ended sequence of empty lines',
                input_value=['\n', '\n', 'non-empty\n', '\n', '\n'],
                expected_value=['\n', '\n', 'non-empty'],
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    Arguments(args.strip_trailing_new_lines()),
                    model_constructor.of_lines(self, case.input_value),
                    arrangement_w_tcds(),
                    expectation_of_successful_execution(
                        symbol_references=asrt.is_empty_sequence,
                        output_lines=case.expected_value,
                        is_identity_transformer=False,
                    )
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
