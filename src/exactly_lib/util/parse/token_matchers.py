from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse.token import Token, TokenMatcher


def is_unquoted_and_equals(value: str) -> TokenMatcher:
    return _Equals(value, True)


def is_option(option: a.OptionName) -> TokenMatcher:
    return _Equals(option_syntax.long_option_syntax(option.long), True)


class _Equals(TokenMatcher):
    def __init__(self,
                 value: str,
                 must_be_unquoted: bool = False):
        self.value = value
        self.must_be_unquoted = must_be_unquoted

    def matches(self, token: Token) -> bool:
        if self.must_be_unquoted and token.is_quoted:
            return False
        return self.value == token.string
