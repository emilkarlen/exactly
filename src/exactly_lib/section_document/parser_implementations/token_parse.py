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
                string: str):
        return tuple.__new__(cls, (token_type, string))

    @property
    def type(self) -> TokenType:
        return self[0]

    @property
    def string(self) -> str:
        return self[1]


def parse_token_on_current_line(source: ParseSource) -> Token:
    """
    Parses a single, mandatory token from remaining part of current line.

    Tokens must be separated by space.

    :param source: Must have a current line. Initial space is consumed. Text for token is consumed.
    :return:
    """
    source.consume_initial_space_on_current_line()
    if source.is_at_eol:
        raise SingleInstructionInvalidArgumentException('Missing token')
    part_of_current_line = source.remaining_part_of_current_line
    source_io = io.StringIO(part_of_current_line)
    lexer = shlex.shlex(source_io, posix=True)
    token_type = _derive_token_type(lexer, source.remaining_part_of_current_line[0])
    try:
        token_string = lexer.get_token()
    except ValueError as ex:
        raise SingleInstructionInvalidArgumentException('Invalid token: ' + str(ex))
    _consume_token_characters(source, source_io)
    return Token(token_type, token_string)


def _derive_token_type(lexer: shlex.shlex, character: str) -> TokenType:
    return TokenType.QUOTED if character in lexer.quotes else TokenType.PLAIN


def _consume_token_characters(source: ParseSource, source_io: io.StringIO):
    num_chars_consumed = source_io.tell()
    if source.remaining_part_of_current_line[num_chars_consumed - 1].isspace():
        num_chars_consumed -= 1
    source.consume_part_of_current_line(num_chars_consumed)
