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
