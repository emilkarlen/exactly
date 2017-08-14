import types

from exactly_lib.help_texts.test_case.instructions import assign_symbol as help_texts
from exactly_lib.instructions.assert_.utils.expression import comprison_structures
from exactly_lib.instructions.assert_.utils.expression import integer_comparators
from exactly_lib.instructions.utils.parse.token_stream_parse_prime import TokenParserPrime
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system_values.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse.token import Token

INTEGER_ARGUMENT = a.Named('INTEGER')
OPERATOR_ARGUMENT = a.Named('OPERATOR')


def parse_integer_comparison_operator_and_rhs(
        parser: TokenParserPrime,
        custom_integer_restriction: types.FunctionType = None
) -> comprison_structures.IntegerComparisonOperatorAndRhs:
    def parse_integer_token_and_return(
            comparison_operator: integer_comparators.ComparisonOperator,
            integer_token: Token) -> comprison_structures.IntegerComparisonOperatorAndRhs:

        integer_resolver = integer_resolver_of(integer_token, custom_integer_restriction)
        return comprison_structures.IntegerComparisonOperatorAndRhs(comparison_operator,
                                                                    integer_resolver)

    token = parser.consume_mandatory_token('Missing comparison expression')

    if not token.is_quoted and token.string in integer_comparators.NAME_2_OPERATOR:
        operator = integer_comparators.NAME_2_OPERATOR[token.string]
        rhs_token = parser.consume_mandatory_token(
            'Missing {INTEGER} expression'.format(INTEGER=INTEGER_ARGUMENT.name)
        )
        return parse_integer_token_and_return(operator, rhs_token)
    else:
        return parse_integer_token_and_return(integer_comparators.EQ,
                                              token)


def integer_resolver_of(value_token: Token,
                        custom_integer_restriction: types.FunctionType = None) -> comprison_structures.IntegerResolver:
    string_resolver = _string_resolver_of(value_token)
    return comprison_structures.IntegerResolver(string_resolver,
                                                custom_integer_restriction)


def _string_resolver_of(value_token: Token) -> StringResolver:
    return parse_string.parse_string_resolver_from_token(
        value_token,
        string_made_up_by_just_strings(
            'The {INTEGER} argument must be made up of just {string_type} values.'.format(
                INTEGER=INTEGER_ARGUMENT.name,
                string_type=help_texts.TYPE_INFO_DICT[ValueType.STRING].type_name,
            )
        ))


def _parse_int_argument(argument) -> int:
    try:
        expected = int(argument)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer')
    if expected < 0 or expected > 255:
        raise SingleInstructionInvalidArgumentException('Argument must be an integer in the interval [0, 255]')
    return expected
