from typing import Generic, Callable, TypeVar, Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens, T
from exactly_lib.util.parse.token import TokenMatcher

PARSE_RESULT = TypeVar('PARSE_RESULT')


class TokenSyntaxSetup(Generic[PARSE_RESULT]):
    def __init__(self,
                 matcher: TokenMatcher,
                 parser_after_token: Callable[[TokenParser], PARSE_RESULT]):
        self.matcher = matcher
        self.parser_after_token = parser_after_token


class ParserWithDefault(Generic[T], ParserFromTokens[T]):
    def __init__(self,
                 syntax_element_name: str,
                 choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                 default: Callable[[TokenParser], PARSE_RESULT],
                 ):
        self._syntax_element_name = syntax_element_name
        self._choices = choices
        self._default = default

    def parse(self, token_parser: TokenParser) -> T:
        return parse_mandatory_choice_with_default(
            token_parser,
            self._syntax_element_name,
            self._choices,
            self._default
        )


def parse_mandatory_choice_with_default(parser: TokenParser,
                                        syntax_element_name: str,
                                        choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                                        default: Callable[[TokenParser], PARSE_RESULT],
                                        ) -> PARSE_RESULT:
    parser.require_existing_valid_head_token(syntax_element_name)
    for syntax_setup in choices:
        if syntax_setup.matcher.matches(parser.head):
            parser.consume_head()
            return syntax_setup.parser_after_token(parser)
    return default(parser)
