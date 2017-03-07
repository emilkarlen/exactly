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
        self._start_pos = 0
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

    def forward(self):
        try:
            s = self._lexer.get_token()
        except ValueError as ex:
            raise TokenSyntaxError(str(ex))
        if s is None:
            self._token = None
        else:
            s_source = self._source[self._start_pos:self._source_io.tell()].strip()
            self._start_pos = self._source_io.tell()
            t = TokenType.QUOTED if s_source[0] in self._lexer.quotes else TokenType.PLAIN
            self._token = Token(t, s, s_source)

#
#
# def p(s):
#     print('[' + s + ']')
#
# ts = TokenStream2(' "b')
# while not ts.is_null:
#     print('----------')
#     p(ts.source[ts.position:])
#     p(ts.head.string)
#     p(ts.head.source_string)
#     p(str(ts.head.type))
#     ts.forward()
