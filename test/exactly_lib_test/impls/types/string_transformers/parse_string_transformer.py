import unittest

from exactly_lib.impls.types.string_transformer import parse_string_transformer as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.expression.test_resources.test_grammars import \
    NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.section_document.test_resources import parse_source


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFailingParse)


class TestFailingParse(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing transformer',
                parse_source.remaining_source(''),
            ),
            NameAndValue(
                'neither a symbol, nor a transformer',
                parse_source.remaining_source(NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parsers(True).full.parse(case.value)
