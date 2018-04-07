import io
import shlex
from enum import Enum

from exactly_lib.util.parse.token import Token, TokenType


class TokenSyntaxError(Exception):
    pass


class LookAheadState(Enum):
    HAS_TOKEN = 0
    NULL = 1
    SYNTAX_ERROR = 2


class TokenStream:
    """
    A stream of tokens with look-ahead of one token.
    """

    def __init__(self, source: str):
        self._source = source
        self._source_io = io.StringIO(source)
        self._lexer = self._new_lexer()
        self._start_pos = 0
        self._head_syntax_error_description = None
        self._head_token = None
        self.consume()

    def _new_lexer(self) -> shlex.shlex:
        lexer = shlex.shlex(self._source_io, posix=True)
        lexer.whitespace_split = True
        return lexer

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_null(self) -> bool:
        return self._head_token is None

    @property
    def is_at_end(self) -> bool:
        return self._start_pos == len(self._source)

    @property
    def look_ahead_state(self) -> LookAheadState:
        if self._head_token:
            return LookAheadState.HAS_TOKEN
        elif not self._head_syntax_error_description:
            return LookAheadState.NULL
        else:
            return LookAheadState.SYNTAX_ERROR

    @property
    def head_syntax_error_description(self) -> str:
        """
        :return: None if look ahead state is not SYNTAX_ERROR
        """
        return self._head_syntax_error_description

    @property
    def head(self) -> Token:
        """
        :rtype None: If is_null
        """
        return self._head_token

    @property
    def position(self) -> int:
        return self._start_pos

    @property
    def remaining_source(self) -> str:
        """Source, including for head, that remains."""
        return self._source[self._start_pos:]

    @property
    def remaining_part_of_current_line(self) -> str:
        """Source, including for head, that remains on the current line."""
        if self._start_pos == len(self._source):
            return ''
        else:
            new_line_pos = self._source.find('\n', self._start_pos)
            if new_line_pos == -1:
                return self._source[self._start_pos:]
            else:
                return self._source[self._start_pos:new_line_pos]

    @property
    def remaining_part_of_current_line_is_empty(self) -> bool:
        remaining = self.remaining_part_of_current_line
        return not remaining or remaining.isspace()

    def consume_remaining_part_of_current_line_as_string(self) -> str:
        """
        Returns the remaining part of the current line, and advances the
        position to the end of line.

        :return: The string given by remaining_part_of_current_line
        """
        return self._consume_remaining_part_of_current_line(False)

    def consume_current_line_as_string_of_remaining_part_of_current_line(self) -> str:
        """
        Returns the remaining part of the current line, and advances the
        position to the following line (if there is one).

        :return: The string given by remaining_part_of_current_line
        """
        return self._consume_remaining_part_of_current_line(True)

    @property
    def remaining_source_after_head(self) -> str:
        """Source, not including for head, that remains."""
        return self._source[self._source_io.tell():]

    def consume(self) -> Token:
        """
        Precondition: not is_null

        Consumes current token and makes the state reflect the following token.

        :raises TokenSyntaxError: The head token has invalid syntax
        """
        if self._head_syntax_error_description:
            raise TokenSyntaxError(self._head_syntax_error_description)

        ret_val = self._head_token
        self._start_pos = self._source_io.tell()
        try:
            s = self._lexer.get_token()
        except ValueError as ex:
            self._head_token = None
            self._head_syntax_error_description = str(ex)
            self._lexer = self._new_lexer()
            return ret_val
        if s is None:
            self._head_token = None
        else:
            self._revert_reading_of_newline()
            s_source = self._source[self._start_pos:self._source_io.tell()].strip()
            t = TokenType.QUOTED if s_source[0] in self._lexer.quotes else TokenType.PLAIN
            self._head_token = Token(t, s, s_source)
        return ret_val

    def _consume_remaining_part_of_current_line(self, do_forward_to_next_line: bool) -> str:
        additional = 1 if do_forward_to_next_line else 0

        if self._start_pos == len(self._source):
            return ''
        else:
            new_line_pos = self._source.find('\n', self._start_pos)
            if new_line_pos == -1:
                ret_val = self._source[self._start_pos:]
                self._head_token = None
                self._head_syntax_error_description = None
                self._start_pos = len(self._source)
                return ret_val
            else:
                ret_val = self._source[self._start_pos:new_line_pos]
                if ret_val and not ret_val.isspace():
                    self._source_io.seek(new_line_pos + additional)
                    self._head_syntax_error_description = None
                    self.consume()
                else:
                    self._start_pos = new_line_pos + additional
                return ret_val

    def _revert_reading_of_newline(self):
        pos = self._source_io.tell()
        if self._source[pos - 1] == '\n':
            self._source_io.seek(pos - 1)
