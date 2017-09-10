import io
import shlex
from enum import Enum

from exactly_lib.util.parse.token import Token, TokenType


class TokenSyntaxError(Exception):
    pass


class LookAheadState(Enum):
    HAS_TOKEN = 0
    NULL = 1


class TokenStream:
    """
    A stream of tokens with look-ahead of one token.
    """

    def __init__(self, source: str):
        self._source = source
        self._source_io = io.StringIO(source)
        self._lexer = shlex.shlex(self._source_io, posix=True)
        self._lexer.whitespace_split = True
        self._start_pos = 0
        self._head_token = None
        self.consume()

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_null(self) -> bool:
        return self._head_token is None

    @property
    def look_ahead_state(self) -> LookAheadState:
        return LookAheadState.HAS_TOKEN if self._head_token else LookAheadState.NULL

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

    def consume_remaining_part_of_current_line_as_plain_string(self) -> str:
        """
        Returns the remaining part of the current line, and advances the
        position to the following line (if there is one).

        :return: The string given by remaining_part_of_current_line
        """
        if self._start_pos == len(self._source):
            return ''
        else:
            new_line_pos = self._source.find('\n', self._start_pos)
            if new_line_pos == -1:
                ret_val = self._source[self._start_pos:]
                self._head_token = None
                self._start_pos = len(self._source)
                return ret_val
            else:
                ret_val = self._source[self._start_pos:new_line_pos]
                self._source_io.seek(new_line_pos + 1)
                self.consume()
                return ret_val

    @property
    def remaining_source_after_head(self) -> str:
        """Source, not including for head, that remains."""
        return self._source[self._source_io.tell():]

    def consume(self) -> Token:
        """
        Precondition: not is_null

        Consumes current token and makes following token the head,
        or makes `is_null` become True if there is no following token.
        """
        ret_val = self._head_token
        self._start_pos = self._source_io.tell()
        try:
            s = self._lexer.get_token()
        except ValueError as ex:
            raise TokenSyntaxError(str(ex))
        if s is None:
            self._head_token = None
        else:
            self._revert_reading_of_newline()
            s_source = self._source[self._start_pos:self._source_io.tell()].strip()
            t = TokenType.QUOTED if s_source[0] in self._lexer.quotes else TokenType.PLAIN
            self._head_token = Token(t, s, s_source)
        return ret_val

    def _revert_reading_of_newline(self):
        pos = self._source_io.tell()
        if self._source[pos - 1] == '\n':
            self._source_io.seek(pos - 1)
