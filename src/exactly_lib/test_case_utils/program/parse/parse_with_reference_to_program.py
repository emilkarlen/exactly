from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.resolvers import program_symbol_resolver
from exactly_lib.test_case_utils.program.resolvers.program_symbol_resolver import ProgramResolverForSymbolReference


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_from_token_parser)


def parse_from_token_parser(parser: TokenParser) -> ProgramResolverForSymbolReference:
    symbol_string = parser.consume_mandatory_unquoted_string(instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME,
                                                             True)
    if not symbol_syntax.is_symbol_name(symbol_string):
        raise SingleInstructionInvalidArgumentException('Invalid syntax of ' +
                                                        instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME +
                                                        ': ' + symbol_string)
    arguments = parse_arguments.parse_from_token_parser(parser)
    return program_symbol_resolver.plain(symbol_string, arguments)
