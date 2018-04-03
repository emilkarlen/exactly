import sys

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import list_resolvers, file_ref_resolvers2
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.test_case_utils.parse import parse_file_ref, parse_list
from exactly_lib.test_case_utils.parse.token_parser_extra import from_parse_source
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.type_system.data import file_refs
from exactly_lib.util.cli_syntax import option_parsing


def parse_from_parse_source(source: ParseSource) -> ExecutableFileWithArgsResolver:
    with from_parse_source(source) as token_parser:
        return parse_from_token_parser(token_parser)


def parse_as_command(token_parser: TokenParser) -> CommandResolver:
    return parse(token_parser.token_stream).as_command


def parse_from_token_parser(token_parser: TokenParser) -> ExecutableFileWithArgsResolver:
    return parse(token_parser.token_stream)


def parse(tokens: TokenStream) -> ExecutableFileWithArgsResolver:
    """
    :param tokens: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens.is_null:
        parse_file_ref.parse_file_ref(tokens, conf=syntax_elements.REL_OPTION_ARG_CONF)  # will raise exception
    if tokens.head.source_string == syntax_elements.LIST_DELIMITER_START:
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
        parse_file_ref.parse_file_ref(tokens, conf=syntax_elements.REL_OPTION_ARG_CONF)  # will raise exception
    token = tokens.head
    if token.is_plain and option_parsing.matches(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME, token.string):
        tokens.consume()
        return file_ref_resolvers2.constant(file_refs.absolute_file_name(sys.executable))
    else:
        return parse_file_ref.parse_file_ref(tokens, conf=syntax_elements.REL_OPTION_ARG_CONF)


def _parse_arguments_and_end_delimiter(tokens: TokenStream) -> ListResolver:
    arguments = []
    while True:
        if tokens.is_null:
            msg = 'Missing end delimiter surrounding executable: %s' % syntax_elements.LIST_DELIMITER_END
            raise SingleInstructionInvalidArgumentException(msg)
        if tokens.head.is_plain and tokens.head.string == syntax_elements.LIST_DELIMITER_END:
            tokens.consume()
            break
        else:
            arguments.append(parse_list.element_of(tokens.head))
        tokens.consume()
    return list_resolvers.from_elements(arguments)
