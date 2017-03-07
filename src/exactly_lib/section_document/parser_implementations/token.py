import enum


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
    def is_plain(self) -> bool:
        return self.type is TokenType.PLAIN

    @property
    def is_quoted(self) -> bool:
        return self.type is TokenType.QUOTED

    @property
    def string(self) -> str:
        return self[1]

    @property
    def source_string(self) -> str:
        return self[2]
