from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser, ParserFromTokenParserBase
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file, parse_system_program, \
    parse_shell_command, parse_with_reference_to_program
from exactly_lib.util import functional


def program_parser(must_be_on_current_line: bool = False,
                   consume_last_line_if_is_at_eol_after_parse: bool = True) -> Parser[ProgramSdv]:
    return _Parser(
        must_be_on_current_line=must_be_on_current_line,
        consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse,
    )


class _Parser(ParserFromTokenParserBase[ProgramSdv]):
    def __init__(self,
                 must_be_on_current_line: bool = False,
                 consume_last_line_if_is_at_eol_after_parse: bool = True,
                 ):
        super().__init__(consume_last_line_if_is_at_eol_after_parse=consume_last_line_if_is_at_eol_after_parse)
        self._must_be_on_current_line = must_be_on_current_line
        self._parser_of_executable_file = parse_executable_file.parser_of_program(
            consume_last_line_if_is_at_eol_after_parse
        )
        self._program_variant_setups = {
            syntax_elements.SHELL_COMMAND_TOKEN:
                parse_shell_command.program_parser(consume_last_line_if_is_at_eol_after_parse
                                                   ).parse_from_token_parser,

            syntax_elements.SYSTEM_PROGRAM_TOKEN:
                parse_system_program.program_parser(consume_last_line_if_is_at_eol_after_parse
                                                    ).parse_from_token_parser,

            syntax_elements.SYMBOL_REF_PROGRAM_TOKEN:
                parse_with_reference_to_program.program_parser(consume_last_line_if_is_at_eol_after_parse
                                                               ).parse_from_token_parser,
        }

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        command_as_program = self._parse_command_and_arguments(parser)

        optional_transformer = parser.consume_and_handle_optional_option3(
            self._parse_transformer,
            string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
        )

        return functional.reduce_optional(
            lambda transformer: command_as_program.new_with_appended_transformations([transformer]),
            command_as_program,
            optional_transformer,
        )

    @staticmethod
    def _parse_transformer(parser: TokenParser) -> StringTransformerSdv:
        from exactly_lib.test_case_utils.string_transformer import parse_string_transformer

        return parse_string_transformer.parse_string_transformer_from_token_parser(parser,
                                                                                   must_be_on_current_line=False)

    def _parse_command_and_arguments(self, parser: TokenParser) -> ProgramSdv:
        return parser.parse_default_or_optional_command(self._parser_of_executable_file.parse_from_token_parser,
                                                        self._program_variant_setups,
                                                        self._must_be_on_current_line)


def parse_program(token_parser: TokenParser,
                  must_be_on_current_line: bool = False) -> ProgramSdv:
    """
    Consumes whole lines, so that the parser will be at the start of the following line, after the parse.
    """
    parser = program_parser(must_be_on_current_line=must_be_on_current_line,
                            consume_last_line_if_is_at_eol_after_parse=True)
    return parser.parse_from_token_parser(token_parser)
