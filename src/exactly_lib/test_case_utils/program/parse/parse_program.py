from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity import types
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_executable_file, parse_shell_command


def program_parser() -> Parser[ProgramResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_program)


def parse_program(parser: TokenParser,
                  initial_transformation: LinesTransformerResolver = None) -> ProgramResolver:
    """
    Consumes whole lines, so that the parser will be at the start of the following line, after the parse.
    """
    program = _parse_simple_program(parser)
    if initial_transformation:
        program = program.new_with_appended_transformations([initial_transformation])

    def parse_transformer(_parser: TokenParser) -> ProgramResolver:
        transformer = parse_lines_transformer.parse_lines_transformer_from_token_parser(_parser)
        parser.require_is_at_eol('Unexpected arguments after ' + types.LINES_TRANSFORMER_TYPE_INFO.name.singular)
        parser.consume_current_line_as_plain_string()
        return program.new_with_appended_transformations([transformer])

    return parser.consume_and_handle_optional_option(program,
                                                     parse_transformer,
                                                     instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)


def _parse_simple_program(parser: TokenParser) -> ProgramResolver:
    if parser.consume_and_return_true_if_first_argument_is_unquoted_and_equals(syntax_elements.SHELL_COMMAND_TOKEN):
        return parse_shell_command.parse_as_program(parser)
    else:
        return parse_executable_file.parse_as_program(parser)
