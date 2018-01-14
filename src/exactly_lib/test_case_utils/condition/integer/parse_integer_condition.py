import types

from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.instruction_arguments import INTEGER_ARGUMENT
from exactly_lib.help_texts.test_case.instructions import define_symbol as help_texts
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    token_parser_with_additional_error_message_format_map
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.integer import integer_resolver
from exactly_lib.test_case_utils.condition.integer.evaluate_integer import python_evaluate, NotAnIntegerException
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher, \
    IntegerMatcherFromComparisonOperator
from exactly_lib.test_case_utils.condition.integer.integer_resolver import IntegerResolver
from exactly_lib.test_case_utils.condition.parse import parse_comparison_operator
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.messages import expected_found
from exactly_lib.util.parse.token import Token

_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION = 'An integer >= 0'


def validator_for_non_negative(actual: int) -> str:
    if actual < 0:
        return expected_found.unexpected_lines(_NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION,
                                               str(actual))
    return None


class IntegerComparisonOperatorAndRightOperand:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs_resolver: IntegerResolver):
        self.right_operand = rhs_resolver
        self.operator = operator


_MISSING_INTEGER_ARGUMENT = 'Missing ' + INTEGER_ARGUMENT.name


def parse_integer_matcher(parser: TokenParser,
                          name_of_lhs: str = 'LHS') -> IntegerMatcher:
    comparison_operator = parse_comparison_operator(parser)
    parser.require_is_not_at_eol(_MISSING_INTEGER_ARGUMENT)
    token = parser.consume_mandatory_token(_MISSING_INTEGER_ARGUMENT)
    try:
        integer_arg = python_evaluate(token.string)
        return IntegerMatcherFromComparisonOperator(name_of_lhs,
                                                    comparison_operator,
                                                    integer_arg)
    except NotAnIntegerException as ex:
        raise SingleInstructionInvalidArgumentException('Not an integer: ' + ex.value_string)


def parse_integer_comparison_operator_and_rhs(
        parser: TokenParser,
        custom_integer_restriction: types.FunctionType = None) -> IntegerComparisonOperatorAndRightOperand:
    my_parser = token_parser_with_additional_error_message_format_map(parser, {'INTEGER': INTEGER_ARGUMENT.name})

    operator = parse_comparison_operator(my_parser)
    integer_token = my_parser.consume_mandatory_token('Missing {INTEGER} expression')

    resolver = integer_resolver_of('expected value', integer_token, custom_integer_restriction)
    return IntegerComparisonOperatorAndRightOperand(operator,
                                                    resolver)


def integer_resolver_of(property_name: str,
                        value_token: Token,
                        custom_integer_restriction: types.FunctionType = None) -> integer_resolver.IntegerResolver:
    string_resolver = _string_resolver_of(value_token)
    return integer_resolver.IntegerResolver(property_name,
                                            string_resolver,
                                            custom_integer_restriction)


def _string_resolver_of(value_token: Token) -> StringResolver:
    return parse_string.parse_string_resolver_from_token(
        value_token,
        string_made_up_by_just_strings(
            'The {INTEGER} argument must be made up of just {string_type} values.'.format(
                INTEGER=syntax_elements.INTEGER_SYNTAX_ELEMENT.argument.name,
                string_type=help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier,
            )
        ))
