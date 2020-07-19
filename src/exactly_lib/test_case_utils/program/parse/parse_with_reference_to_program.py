from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser, ParserFromTokenParserBase
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program.parse import parse_arguments
from exactly_lib.test_case_utils.program.sdvs import program_symbol_sdv
from exactly_lib.test_case_utils.program.sdvs.program_symbol_sdv import ProgramSdvForSymbolReference


def program_parser(consume_last_line_if_is_at_eol_after_parse: bool) -> Parser[ProgramSdv]:
    return _ParseAsProgram(consume_last_line_if_is_at_eol_after_parse)


def parse_from_token_parser(token_parser: TokenParser) -> ProgramSdvForSymbolReference:
    parser = _ParseAsProgram(consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)


class _ParseAsProgram(ParserFromTokenParserBase[ProgramSdvForSymbolReference]):
    def __init__(self, consume_last_line_if_is_at_eol_after_parse: bool):
        super().__init__(
            consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse
        )
        self._arguments_parser = parse_arguments.parser(consume_last_line_if_is_at_eol_after_parse)

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdvForSymbolReference:
        symbol_string = self._symbol_string(parser)

        arguments = self._arguments_parser.parse_from_token_parser(parser)

        return program_symbol_sdv.plain(symbol_string, arguments)

    def _symbol_string(self, parser: TokenParser) -> str:
        symbol_string = parser.consume_mandatory_unquoted_string(
            instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME,
            True
        )
        if not symbol_syntax.is_symbol_name(symbol_string):
            raise SingleInstructionInvalidArgumentException(
                'Invalid syntax of ' +
                instruction_arguments.SYMBOL_SYNTAX_ELEMENT_NAME +
                ': ' + symbol_string
            )

        return symbol_string
