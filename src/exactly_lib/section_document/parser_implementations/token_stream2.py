import io
import shlex

from exactly_lib.section_document.parser_implementations.token import Token, TokenType


class TokenSyntaxError(Exception):
    pass


class TokenStream2:
    def __init__(self, source: str):
        self._source = source
        self._source_io = io.StringIO(source)
        self._lexer = shlex.shlex(self._source_io, posix=True)
        self._lexer.whitespace_split = True
        self._token = None
        self.forward()

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_null(self) -> bool:
        return self._token is None

    @property
    def head(self) -> Token:
        return self._token

    @property
    def position(self) -> int:
        return self._source_io.tell()

    @property
    def remaining_source(self) -> str:
        return self._source[self._source_io.tell():]

    def forward(self):
        """
        Precondition: not is_null

        Consumes current token and makes following token the head,
        or makes `is_null` become True if there is no following token.
        """
        pos_before = self._source_io.tell()
        try:
            s = self._lexer.get_token()
        except ValueError as ex:
            raise TokenSyntaxError(str(ex))
        if s is None:
            self._token = None
        else:
            s_source = self._source[pos_before:self._source_io.tell()].strip()
            t = TokenType.QUOTED if s_source[0] in self._lexer.quotes else TokenType.PLAIN
            self._token = Token(t, s, s_source)
