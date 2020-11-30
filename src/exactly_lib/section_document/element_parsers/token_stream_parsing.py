from typing import Generic, Callable, TypeVar, Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.util.parse.token import TokenMatcher, Token

PARSE_RESULT = TypeVar('PARSE_RESULT')


class TokenSyntaxSetup(Generic[PARSE_RESULT]):
    def __init__(self,
                 matcher: TokenMatcher,
                 parser_after_token: Callable[[TokenParser], PARSE_RESULT]):
        self.matcher = matcher
        self.parser_after_token = parser_after_token


class TokenSyntaxSetup2(Generic[PARSE_RESULT]):
    def __init__(self,
                 matcher: TokenMatcher,
                 parser_after_token: Callable[[Token, TokenParser], PARSE_RESULT]):
        self.matcher = matcher
        self.parser_after_token = parser_after_token


class ParserOfMandatoryChoice(Generic[PARSE_RESULT], ParserFromTokens[PARSE_RESULT]):
    def __init__(self,
                 syntax_element: str,
                 choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                 ):
        self._syntax_element = syntax_element
        self._choices = choices

    def parse(self, token_parser: TokenParser) -> PARSE_RESULT:
        return parse_mandatory_choice(
            token_parser,
            self._syntax_element,
            self._choices,
        )


class ParserOfMandatoryChoiceWithDefault(Generic[PARSE_RESULT], ParserFromTokens[PARSE_RESULT]):
    def __init__(self,
                 syntax_element: str,
                 choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                 default: Callable[[TokenParser], PARSE_RESULT],
                 ):
        self._syntax_element = syntax_element
        self._choices = choices
        self._default = default

    def parse(self, token_parser: TokenParser) -> PARSE_RESULT:
        return parse_mandatory_choice_with_default(
            token_parser,
            self._syntax_element,
            self._choices,
            self._default,
        )


class ParserOfMandatoryChoiceWithDefault2(Generic[PARSE_RESULT], ParserFromTokens[PARSE_RESULT]):
    def __init__(self,
                 syntax_element: str,
                 choices: Sequence[TokenSyntaxSetup2[PARSE_RESULT]],
                 default: Callable[[TokenParser], PARSE_RESULT],
                 ):
        self._syntax_element = syntax_element
        self._choices = choices
        self._default = default

    def parse(self, token_parser: TokenParser) -> PARSE_RESULT:
        return parse_mandatory_choice_with_default2(
            token_parser,
            self._syntax_element,
            self._choices,
            self._default,
        )


class ParserOfOptionalChoiceWithDefault(Generic[PARSE_RESULT], ParserFromTokens[PARSE_RESULT]):
    def __init__(self,
                 choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                 default: Callable[[TokenParser], PARSE_RESULT],
                 ):
        self._choices = choices
        self._default = default

    def parse(self, token_parser: TokenParser) -> PARSE_RESULT:
        return parse_optional_choice_with_default(
            token_parser,
            self._choices,
            self._default,
        )


def parse_mandatory_choice(token_parser: TokenParser,
                           syntax_element: str,
                           choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                           ) -> PARSE_RESULT:
    token_parser.require_existing_valid_head_token(syntax_element)
    for syntax_setup in choices:
        if syntax_setup.matcher.matches(token_parser.head):
            token_parser.consume_head()
            return syntax_setup.parser_after_token(token_parser)
    return token_parser.report_missing(syntax_element)


def parse_mandatory_choice_with_default(token_parser: TokenParser,
                                        syntax_element: str,
                                        choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                                        default: Callable[[TokenParser], PARSE_RESULT],
                                        ) -> PARSE_RESULT:
    token_parser.require_existing_valid_head_token(syntax_element)
    for syntax_setup in choices:
        if syntax_setup.matcher.matches(token_parser.head):
            token_parser.consume_head()
            return syntax_setup.parser_after_token(token_parser)
    return default(token_parser)


def parse_mandatory_choice_with_default2(token_parser: TokenParser,
                                         syntax_element: str,
                                         choices: Sequence[TokenSyntaxSetup2[PARSE_RESULT]],
                                         default: Callable[[TokenParser], PARSE_RESULT],
                                         ) -> PARSE_RESULT:
    token_parser.require_existing_valid_head_token(syntax_element)
    head = token_parser.head
    for syntax_setup in choices:
        if syntax_setup.matcher.matches(head):
            token_parser.consume_head()
            return syntax_setup.parser_after_token(head, token_parser)
    return default(token_parser)


def parse_optional_choice_with_default(token_parser: TokenParser,
                                       choices: Sequence[TokenSyntaxSetup[PARSE_RESULT]],
                                       default: Callable[[TokenParser], PARSE_RESULT],
                                       ) -> PARSE_RESULT:
    if token_parser.has_valid_head_token_on_current_line():
        head_token = token_parser.head
        for syntax_setup in choices:
            if syntax_setup.matcher.matches(head_token):
                token_parser.consume_head()
                return syntax_setup.parser_after_token(token_parser)
    return default(token_parser)
