from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.condition.comparators import ComparisonOperator
from exactly_lib.impls.types.condition.syntax import OPERATOR_ARGUMENT
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens


class ComparisonOperatorParser(ParserFromTokens[ComparisonOperator]):
    """Parses an :class:`ComparisonOperator` on current or following line"""

    def parse(self, token_parser: TokenParser) -> ComparisonOperator:
        token_string = token_parser.consume_mandatory_unquoted_string(OPERATOR_ARGUMENT.name, False)

        if token_string not in comparators.NAME_2_OPERATOR:
            raise SingleInstructionInvalidArgumentException('Invalid {op}: {actual}'.format(op=OPERATOR_ARGUMENT.name,
                                                                                            actual=token_string))

        return comparators.NAME_2_OPERATOR[token_string]
