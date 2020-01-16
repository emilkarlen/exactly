import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.test_case_utils.expression.test_resources import \
    NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseLineTransformer)


class TestParseLineTransformer(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing transformer',
                parse_source.remaining_source(''),
            ),
            NameAndValue(
                'neither a symbol, nor a transformer',
                parse_source.remaining_source(NOT_A_SIMPLE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(case.value)
