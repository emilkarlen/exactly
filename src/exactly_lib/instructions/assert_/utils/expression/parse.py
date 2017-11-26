import types

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help_texts.instruction_arguments import INTEGER_ARGUMENT
from exactly_lib.help_texts.test_case.instructions import define_symbol as help_texts
from exactly_lib.instructions.assert_.utils.expression import comparators, integer_resolver
from exactly_lib.instructions.assert_.utils.expression.integer_resolver import IntegerResolver
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.symbol.data.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.test_case_utils import negation_of_predicate
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.messages import expected_found
from exactly_lib.util.parse.token import Token
from exactly_lib.util.textformat.structure import structures as docs

OPERATOR_ARGUMENT = a.Named('OPERATOR')

NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION = 'An integer >= 0'

MANDATORY_OPERATOR_ARGUMENT = a.Single(a.Multiplicity.MANDATORY,
                                       OPERATOR_ARGUMENT)

MANDATORY_INTEGER_ARGUMENT = a.Single(a.Multiplicity.MANDATORY,
                                      INTEGER_ARGUMENT)

ARGUMENTS_FOR_COMPARISON_WITH_OPTIONAL_OPERATOR = [
    a.Single(a.Multiplicity.OPTIONAL, OPERATOR_ARGUMENT),
    MANDATORY_INTEGER_ARGUMENT,
]


def syntax_element_descriptions(integer_text: str = 'An integer.') -> list:
    operators_list = ' '.join(sorted(comparators.NAME_2_OPERATOR.keys()))
    operator_text = 'One of ' + operators_list
    return [
        SyntaxElementDescription(OPERATOR_ARGUMENT.name,
                                 docs.paras(operator_text)),
        SyntaxElementDescription(INTEGER_ARGUMENT.name,
                                 docs.paras(integer_text)),
    ]


def syntax_element_descriptions_with_negation_operator(
        integer_text: str = 'An integer') -> list:
    return [negation_of_predicate.syntax_element_description()] + syntax_element_descriptions(integer_text)


def validator_for_non_negative(actual: int) -> str:
    if actual < 0:
        return expected_found.unexpected_lines(NON_NEGATIVE_INTEGER_ARGUMENT_DESCRIPTION,
                                               str(actual))
    return None


class IntegerComparisonOperatorAndRightOperand:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs_resolver: IntegerResolver):
        self.right_operand = rhs_resolver
        self.operator = operator


def parse_integer_comparison_operator_and_rhs(
        parser: TokenParserPrime,
        custom_integer_restriction: types.FunctionType = None
) -> IntegerComparisonOperatorAndRightOperand:
    def parse_integer_token_and_return(
            comparison_operator: comparators.ComparisonOperator,
            integer_token: Token) -> IntegerComparisonOperatorAndRightOperand:

        resolver = integer_resolver_of('expected value', integer_token, custom_integer_restriction)
        return IntegerComparisonOperatorAndRightOperand(comparison_operator,
                                                        resolver)

    token = parser.consume_mandatory_token('Missing comparison expression')

    if not token.is_quoted and token.string in comparators.NAME_2_OPERATOR:
        operator = comparators.NAME_2_OPERATOR[token.string]
        rhs_token = parser.consume_mandatory_token(
            'Missing {INTEGER} expression'.format(INTEGER=INTEGER_ARGUMENT.name)
        )
        return parse_integer_token_and_return(operator, rhs_token)
    else:
        return parse_integer_token_and_return(comparators.EQ,
                                              token)


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
                INTEGER=INTEGER_ARGUMENT.name,
                string_type=help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier,
            )
        ))
