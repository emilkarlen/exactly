from typing import Optional

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.instruction_arguments import INTEGER_ARGUMENT
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer import integer_resolver
from exactly_lib.test_case_utils.condition.integer.integer_resolver import IntegerResolver
from exactly_lib.test_case_utils.condition.integer.integer_value import CustomIntegerValidator, IntegerValue
from exactly_lib.test_case_utils.condition.parse import parse_comparison_operator
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util import strings
from exactly_lib.util.parse.token import Token


class IntegerComparisonOperatorAndRightOperandResolver:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs_resolver: IntegerResolver):
        self.right_operand = rhs_resolver
        self.operator = operator


class IntegerComparisonOperatorAndRightOperandValue:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs_value: IntegerValue):
        self.right_operand = rhs_value
        self.operator = operator


def parse_integer_comparison_operator_and_rhs(
        parser: TokenParser,
        custom_integer_restriction: Optional[CustomIntegerValidator] = None,
) -> IntegerComparisonOperatorAndRightOperandResolver:
    my_parser = token_parser_with_additional_error_message_format_map(parser, {'INTEGER': INTEGER_ARGUMENT.name})

    operator = parse_comparison_operator(my_parser)
    integer_token = my_parser.consume_mandatory_token('Missing {INTEGER} expression')

    resolver = integer_resolver_of(integer_token, custom_integer_restriction)
    return IntegerComparisonOperatorAndRightOperandResolver(operator,
                                                            resolver)


def integer_resolver_of(value_token: Token,
                        custom_integer_restriction: Optional[CustomIntegerValidator] = None
                        ) -> integer_resolver.IntegerResolver:
    string_resolver = _string_resolver_of(value_token)
    return integer_resolver.IntegerResolver(string_resolver,
                                            custom_integer_restriction)


def _string_resolver_of(value_token: Token) -> StringResolver:
    return parse_string.parse_string_resolver_from_token(
        value_token,
        _REFERENCE_RESTRICTIONS,
    )


_REFERENCE_RESTRICTIONS = string_made_up_by_just_strings(
    text_docs.single_pre_formatted_line_object(
        strings.FormatMap(
            'The {INTEGER} argument must be made up of just {string_type} values.',
            {
                'INTEGER': syntax_elements.INTEGER_SYNTAX_ELEMENT.argument.name,
                'string_type': help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier
            }
        )
    )
)
