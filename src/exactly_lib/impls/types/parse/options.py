from typing import Generic, Optional, TypeVar

from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.cli_syntax.elements import argument as a


def option_is_present(option: a.OptionName) -> Parser[bool]:
    return _OptionalOptionParser(option)


class _OptionalOptionParser(parsers.ParserFromTokenParserBase[bool]):
    def __init__(self, option: a.OptionName):
        super().__init__(False, False)
        self._option = option

    def parse_from_token_parser(self, parser: TokenParser) -> bool:
        return parser.consume_optional_option(self._option)


T = TypeVar('T')


class OptionalOptionWMandatoryArgumentParser(Generic[T],
                                             parsers.ParserFromTokenParserBase[Optional[T]]):
    def __init__(self,
                 option: a.OptionName,
                 argument_parser: Parser[T],
                 ):
        super().__init__(False, False)
        self._option = option
        self._argument_parser = argument_parser

    def parse_from_token_parser(self, parser: TokenParser) -> Optional[T]:
        return parser.consume_and_handle_optional_option3(
            self._argument_parser.parse_from_token_parser,
            self._option,
        )
