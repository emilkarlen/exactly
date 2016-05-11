from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException

LIST_DELIMITER_START = '('
LIST_DELIMITER_END = ')'
PARSE_FILE_REF_CONFIGURATION = parse_file_ref.DEFAULT_CONFIG


def parse(tokens: TokenStream) -> (ExecutableFile, TokenStream):
    """
    :param tokens: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    if tokens.is_null:
        parse_file_ref.parse_file_ref(tokens, conf=PARSE_FILE_REF_CONFIGURATION)  # will raise exception
    if tokens.head == LIST_DELIMITER_START:
        (the_file_ref, remaining_tokens) = parse_file_ref.parse_file_ref(tokens.tail,
                                                                         conf=PARSE_FILE_REF_CONFIGURATION)
        (exe_argument_list, tail_tokens) = _parse_arguments_and_end_delimiter(remaining_tokens)
        return ExecutableFile(the_file_ref, exe_argument_list), tail_tokens
    else:
        (the_file_ref, remaining_tokens) = parse_file_ref.parse_file_ref(tokens,
                                                                         conf=PARSE_FILE_REF_CONFIGURATION)
        return ExecutableFile(the_file_ref, []), remaining_tokens


def _parse_arguments_and_end_delimiter(tokens: TokenStream) -> (list, TokenStream):
    arguments = []
    while True:
        if tokens.is_null:
            msg = 'Missing end delimiter surrounding executable: %s' % LIST_DELIMITER_END
            raise SingleInstructionInvalidArgumentException(msg)
        if tokens.head == LIST_DELIMITER_END:
            return arguments, tokens.tail
        arguments.append(tokens.head)
        tokens = tokens.tail
