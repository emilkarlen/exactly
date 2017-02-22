import enum
import io
import shlex

from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


class TokenType(enum.Enum):
    PLAIN = 0
    QUOTED = 1


class Token(tuple):
    def __new__(cls,
                token_type: TokenType,
                string: str,
                source_string: str = None):
        return tuple.__new__(cls, (token_type,
                                   string,
                                   source_string if source_string is not None else string))

    @property
    def type(self) -> TokenType:
        return self[0]

    @property
    def string(self) -> str:
        return self[1]

    @property
    def source_string(self) -> str:
        return self[2]


def parse_token_or_none_on_current_line(source: ParseSource) -> Token:
    """
    Parses a single, optional token from remaining part of current line.

    Tokens must be separated by space.

    :param source: Must have a current line. Initial space is consumed. Text for token is consumed.
    :raise SingleInstructionInvalidArgumentException: The token has invalid syntax
    """
    source.consume_initial_space_on_current_line()
    if source.is_at_eol:
        return None
    part_of_current_line = source.remaining_part_of_current_line
    source_io = io.StringIO(part_of_current_line)
    lexer = shlex.shlex(source_io, posix=True)
    lexer.whitespace_split = True
    token_type = _derive_token_type(lexer, source.remaining_part_of_current_line[0])
    try:
        token_string = lexer.get_token()
    except ValueError as ex:
        raise SingleInstructionInvalidArgumentException('Invalid token: ' + str(ex))
    source_string = _get_source_string_and_consume_token_characters(source, source_io)
    return Token(token_type, token_string, source_string)


def parse_token_on_current_line(source: ParseSource) -> Token:
    """
    Parses a single, mandatory token from remaining part of current line.

    Tokens must be separated by space.

    :param source: Must have a current line. Initial space is consumed. Text for token is consumed.
    :raise SingleInstructionInvalidArgumentException: There is no token
    :raise SingleInstructionInvalidArgumentException: The token has invalid syntax
    """
    token = parse_token_or_none_on_current_line(source)
    if token is None:
        raise SingleInstructionInvalidArgumentException('Missing argument')
    return token


def parse_plain_token_on_current_line(source: ParseSource) -> Token:
    """
    Parses a single, mandatory plain (unquoted) token from remaining part of current line.

    Tokens must be separated by space.

    :param source: Must have a current line. Initial space is consumed. Text for token is consumed.
    :raise SingleInstructionInvalidArgumentException: There is no token
    :raise SingleInstructionInvalidArgumentException: The token has invalid syntax
    """
    token = parse_token_or_none_on_current_line(source)
    if token is None:
        raise SingleInstructionInvalidArgumentException('Missing argument')
    if token.type is TokenType.QUOTED:
        raise SingleInstructionInvalidArgumentException('Argument must not be quoted: ' + token.source_string)
    return token


def _derive_token_type(lexer: shlex.shlex, character: str) -> TokenType:
    return TokenType.QUOTED if character in lexer.quotes else TokenType.PLAIN


def _get_source_string_and_consume_token_characters(source: ParseSource,
                                                    source_io: io.StringIO) -> str:
    num_chars_consumed = source_io.tell()
    if source.remaining_part_of_current_line[num_chars_consumed - 1].isspace():
        num_chars_consumed -= 1
    ret_val = source.remaining_source[:num_chars_consumed]
    source.consume_part_of_current_line(num_chars_consumed)
    return ret_val
