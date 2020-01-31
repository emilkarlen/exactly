from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file, parse_system_program, \
    parse_shell_command, parse_with_reference_to_program
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer


def program_parser() -> Parser[ProgramSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_program)


def parse_program(parser: TokenParser,
                  must_be_on_current_line=False) -> ProgramSdv:
    """
    Consumes whole lines, so that the parser will be at the start of the following line, after the parse.
    """
    program = _parse_simple_program(parser,
                                    must_be_on_current_line)

    def parse_transformer(_parser: TokenParser) -> ProgramSdv:
        transformer = parse_string_transformer.parse_string_transformer_from_token_parser(_parser)
        parser.require_is_at_eol('Unexpected arguments after ' + types.STRING_TRANSFORMER_TYPE_INFO.name.singular)
        parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return program.new_with_appended_transformations([transformer])

    return parser.consume_and_handle_optional_option(program,
                                                     parse_transformer,
                                                     string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def _parse_simple_program(parser: TokenParser,
                          must_be_on_current_line=False) -> ProgramSdv:
    return parser.parse_default_or_optional_command(parse_executable_file.parse_as_program,
                                                    _PROGRAM_VARIANT_SETUPS,
                                                    must_be_on_current_line)


_PROGRAM_VARIANT_SETUPS = {
    syntax_elements.SHELL_COMMAND_TOKEN: parse_shell_command.parse_as_program,
    syntax_elements.SYSTEM_PROGRAM_TOKEN: parse_system_program.parse_as_program,
    syntax_elements.SYMBOL_REF_PROGRAM_TOKEN: parse_with_reference_to_program.parse_from_token_parser,
}
