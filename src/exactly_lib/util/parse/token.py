import enum


class TokenType(enum.Enum):
    PLAIN = 0
    QUOTED = 1


class QuoteType(enum.Enum):
    SOFT = 1
    HARD = 2


SOFT_QUOTE_CHAR = '"'
HARD_QUOTE_CHAR = '\''

QUOTE_CHARS = frozenset([SOFT_QUOTE_CHAR,
                         HARD_QUOTE_CHAR])


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
    def is_plain(self) -> bool:
        return self.type is TokenType.PLAIN

    @property
    def is_quoted(self) -> bool:
        return self.type is TokenType.QUOTED

    @property
    def quote_type(self) -> QuoteType:
        """
        Precontition: is_quoted
        """
        return QuoteType.SOFT if self[2][0] == SOFT_QUOTE_CHAR else QuoteType.HARD

    @property
    def is_hard_quote_type(self) -> bool:
        """
        Precontition: is_quoted
        """
        return self[2][0] == HARD_QUOTE_CHAR

    @property
    def string(self) -> str:
        return self[1]

    @property
    def source_string(self) -> str:
        return self[2]
