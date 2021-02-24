from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.condition import parse as parse_condition
from exactly_lib.impls.types.integer import integer_sdv
from exactly_lib.impls.types.integer.integer_ddv import CustomIntegerValidator
from exactly_lib.impls.types.integer.integer_sdv import IntegerSdv
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map, ParserFromTokens
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.util.messages import expected_found
from exactly_lib.util.parse.token import Token
from exactly_lib.util.str_ import str_constructor


class IntegerComparisonOperatorAndRightOperandSdv:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs_operand: IntegerSdv):
        self.rhs_operand = rhs_operand
        self.operator = operator


class ComparisonOperatorAndRhsParser(ParserFromTokens[IntegerComparisonOperatorAndRightOperandSdv]):
    """Parses an :class:`IntegerComparisonOperatorAndRightOperandSdv` on current or following line"""

    OPERATOR_PARSER = parse_condition.ComparisonOperatorParser()

    def __init__(self,
                 custom_integer_restriction: Optional[CustomIntegerValidator] = None,
                 ):
        self._integer_parser = MandatoryIntegerParser(custom_integer_restriction)

    def parse(self, token_parser: TokenParser) -> IntegerComparisonOperatorAndRightOperandSdv:
        operator = self.OPERATOR_PARSER.parse(token_parser)
        integer = self._integer_parser.parse(token_parser)
        return IntegerComparisonOperatorAndRightOperandSdv(operator, integer)


class MandatoryIntegerParser(ParserFromTokens[IntegerSdv]):
    def __init__(self,
                 custom_integer_restriction: Optional[CustomIntegerValidator] = None,
                 integer_argument_name_in_err_msg: str = syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
                 ):
        self._custom_integer_restriction = custom_integer_restriction
        self._integer_argument_name_in_err_msg = integer_argument_name_in_err_msg

    def parse(self, token_parser: TokenParser) -> IntegerSdv:
        my_parser = token_parser_with_additional_error_message_format_map(token_parser, {
            'INTEGER': self._integer_argument_name_in_err_msg})
        integer_token = my_parser.consume_mandatory_token('Missing {INTEGER} expression')
        return integer_sdv_of(integer_token, self._custom_integer_restriction)


def integer_sdv_of(value_token: Token,
                   custom_integer_restriction: Optional[CustomIntegerValidator] = None
                   ) -> integer_sdv.IntegerSdv:
    string_sdv = _string_sdv_of(value_token)
    return integer_sdv.IntegerSdv(string_sdv,
                                  custom_integer_restriction)


def _string_sdv_of(value_token: Token) -> StringSdv:
    return parse_string.parse_string_sdv_from_token(
        value_token,
        _REFERENCE_RESTRICTIONS,
    )


_REFERENCE_RESTRICTIONS = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'The {INTEGER} argument must be made up of just {string_type} values.',
            {
                'INTEGER': syntax_elements.INTEGER_SYNTAX_ELEMENT.argument.name,
                'string_type': help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier
            }
        )
    )
)


def validator_for_non_negative(actual: int) -> Optional[TextRenderer]:
    if actual < 0:
        return expected_found.unexpected_lines(_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION,
                                               str(actual))
    return None


_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION = 'An integer >= 0'
