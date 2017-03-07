import sys

from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case import file_ref
from exactly_lib.test_case import file_refs
from exactly_lib.util.cli_syntax import option_parsing
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax

LIST_DELIMITER_START = '('
LIST_DELIMITER_END = ')'
PARSE_FILE_REF_CONFIGURATION = parse_file_ref.DEFAULT_CONFIG

PYTHON_EXECUTABLE_OPTION_NAME = argument.OptionName(long_name='python')
PYTHON_EXECUTABLE_OPTION_STRING = long_option_syntax(PYTHON_EXECUTABLE_OPTION_NAME.long)


def parse(tokens: TokenStream2) -> ExecutableFile:
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
        return ExecutableFile(the_file_ref, exe_argument_list)
    else:
        the_file_ref = _parse_exe_file_ref(tokens)
        return ExecutableFile(the_file_ref, [])


def _parse_exe_file_ref(tokens: TokenStream2) -> file_ref.FileRef:
    if tokens.is_null:
        parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)  # will raise exception
    token = tokens.head
    if token.is_plain and option_parsing.matches(PYTHON_EXECUTABLE_OPTION_NAME, token.string):
        tokens.consume()
        return file_refs.absolute_file_name(sys.executable)
    else:
        return parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)


def _parse_arguments_and_end_delimiter(tokens: TokenStream2) -> list:
    arguments = []
    while True:
        if tokens.is_null:
            msg = 'Missing end delimiter surrounding executable: %s' % LIST_DELIMITER_END
            raise SingleInstructionInvalidArgumentException(msg)
        if tokens.head.is_plain and tokens.head.string == LIST_DELIMITER_END:
            tokens.consume()
            return arguments
        arguments.append(tokens.head.string)
        tokens.consume()
