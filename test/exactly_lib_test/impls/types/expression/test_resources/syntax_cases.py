from typing import Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source


class TestCaseGeneratorForParenthesis:
    def __init__(self,
                 valid_symbol_name_and_not_valid_primitive_or_operator: str,
                 not_a_valid_symbol_name_nor_valid_primitive_or_operator: str,
                 ):
        self.not_a_valid_symbol_name_nor_valid_primitive_or_operator = \
            not_a_valid_symbol_name_nor_valid_primitive_or_operator
        self.valid_symbol_name_and_not_valid_primitive_or_operator = \
            valid_symbol_name_and_not_valid_primitive_or_operator

    def parse_should_fail_when_syntax_is_invalid(self) -> Sequence[NameAndValue[ParseSource]]:
        return [
            NameAndValue(
                'eof after (',
                remaining_source('(  ')
            ),
            NameAndValue(
                'missing )',
                remaining_source('(  {symbol_name}'.format(
                    symbol_name=self.valid_symbol_name_and_not_valid_primitive_or_operator)
                )
            ),
            NameAndValue(
                'missing space after (',
                remaining_source('({symbol_name} )'.format(
                    symbol_name=self.valid_symbol_name_and_not_valid_primitive_or_operator)
                )
            ),
            NameAndValue(
                'invalid expression inside ()',
                remaining_source('( {invalid} )'.format(
                    invalid=self.not_a_valid_symbol_name_nor_valid_primitive_or_operator)
                )
            ),
        ]
