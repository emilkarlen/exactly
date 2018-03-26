import sys

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_resolvers, file_ref_resolvers2
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.test_case_utils.parse import parse_file_ref, parse_list
from exactly_lib.test_case_utils.parse.token_parser_extra import from_parse_source
from exactly_lib.test_case_utils.program.command import command_resolvers
from exactly_lib.test_case_utils.program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.type_system.data import file_refs
from exactly_lib.util.cli_syntax import option_parsing
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

LIST_DELIMITER_START = '('
LIST_DELIMITER_END = ')'
PARSE_FILE_REF_CONFIGURATION = parse_file_ref.ALL_REL_OPTIONS_CONFIG

PYTHON_EXECUTABLE_OPTION_NAME = argument.OptionName(long_name='python')
PYTHON_EXECUTABLE_OPTION_STRING = long_option_syntax(PYTHON_EXECUTABLE_OPTION_NAME.long)


def parse_from_parse_source(source: ParseSource) -> ExecutableFileWithArgsResolver:
    with from_parse_source(source) as token_parser:
        return parse_from_token_parser(token_parser)


def parse_from_parse_source_new(source: ParseSource) -> CommandResolver:
    with from_parse_source(source) as token_parser:
        return parse_from_token_parser_new(token_parser)


def parse_from_token_parser_new(token_parser: TokenParser) -> CommandResolver:
    exe_file = parse(token_parser.token_stream)
    command_resolver = command_resolvers.for_executable_file(exe_file.executable_file)
    return command_resolver.new_with_additional_arguments(exe_file.arguments)


def parse_from_token_parser(token_parser: TokenParser) -> ExecutableFileWithArgsResolver:
    return parse(token_parser.token_stream)


def parse(tokens: TokenStream) -> ExecutableFileWithArgsResolver:
    """
    :param tokens: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens.is_null:
        parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)  # will raise exception
    if tokens.head.source_string == LIST_DELIMITER_START:
        tokens.consume()
        the_file_ref = _parse_exe_file_ref(tokens)
        exe_argument_list = _parse_arguments_and_end_delimiter(tokens)
        return ExecutableFileWithArgsResolver(the_file_ref, exe_argument_list)
    else:
        the_file_ref = _parse_exe_file_ref(tokens)
        return ExecutableFileWithArgsResolver(the_file_ref,
                                              list_resolvers.empty())


def _parse_exe_file_ref(tokens: TokenStream) -> FileRefResolver:
    if tokens.is_null:
        parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)  # will raise exception
    token = tokens.head
    if token.is_plain and option_parsing.matches(PYTHON_EXECUTABLE_OPTION_NAME, token.string):
        tokens.consume()
        return file_ref_resolvers2.constant(file_refs.absolute_file_name(sys.executable))
    else:
        return parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)


def _parse_arguments_and_end_delimiter(tokens: TokenStream) -> ListResolver:
    arguments = []
    while True:
        if tokens.is_null:
            msg = 'Missing end delimiter surrounding executable: %s' % LIST_DELIMITER_END
            raise SingleInstructionInvalidArgumentException(msg)
        if tokens.head.is_plain and tokens.head.string == LIST_DELIMITER_END:
            tokens.consume()
            break
        else:
            arguments.append(parse_list.element_of(tokens.head))
        tokens.consume()
    return list_resolvers.from_elements(arguments)
