from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.condition.syntax import OPERATOR_ARGUMENT


def parse_comparison_operator(parser: TokenParserPrime) -> comparators.ComparisonOperator:
    token_string = parser.consume_mandatory_unquoted_string(OPERATOR_ARGUMENT.name, True)

    if token_string not in comparators.NAME_2_OPERATOR:
        raise SingleInstructionInvalidArgumentException('Invalid {op}: {actual}'.format(op=OPERATOR_ARGUMENT.name,
                                                                                        actual=token_string))

    return comparators.NAME_2_OPERATOR[token_string]
