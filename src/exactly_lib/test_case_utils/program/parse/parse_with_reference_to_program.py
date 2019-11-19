from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.sdvs import program_symbol_sdv
from exactly_lib.test_case_utils.program.sdvs.program_symbol_sdv import ProgramSdvForSymbolReference


def program_parser() -> Parser[ProgramSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_from_token_parser)


def parse_from_token_parser(parser: TokenParser) -> ProgramSdvForSymbolReference:
    symbol_string = parser.consume_mandatory_unquoted_string(instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME,
                                                             True)
    if not symbol_syntax.is_symbol_name(symbol_string):
        raise SingleInstructionInvalidArgumentException('Invalid syntax of ' +
                                                        instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME +
                                                        ': ' + symbol_string)
    arguments = parse_arguments.parse_from_token_parser(parser)
    return program_symbol_sdv.plain(symbol_string, arguments)
