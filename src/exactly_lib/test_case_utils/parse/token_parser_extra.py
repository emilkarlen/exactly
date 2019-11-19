from contextlib import contextmanager

from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.test_case_utils.parse import parse_path
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration


class TokenParserExtra(TokenParser):
    """
    Utility for implementing parsers backed by a :class:`TokenStream`,

    with "extra" support for parsing value types used by Exactly.
    """

    def __init__(self, token_stream: TokenStream, error_message_format_map: dict = None):
        """
        
        :param token_stream: Token stream to read tokens from.
        :param error_message_format_map: Map to pass to string.format_map as the map argument.
        """
        super().__init__(token_stream, error_message_format_map)

    def consume_path(self, conf: RelOptionArgumentConfiguration) -> PathSdv:
        return parse_path.parse_path(self._token_stream, conf)


def new_token_parser(source: str,
                     error_message_format_map: dict = None) -> TokenParserExtra:
    """
    Constructs a :class:`TokenParser`
    :argument error_message_format_map: strings that are replaced in error messages
    via :func:`str#format`
    :type error_message_format_map: dict str -> str
    :raises :class:`SingleInstructionInvalidArgumentException` Source has invalid syntax
    """
    return TokenParserExtra(new_token_stream(source),
                            error_message_format_map)


@contextmanager
def from_parse_source(parse_source: ParseSource):
    """
    Gives a :class:`TokenParser` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParser` is the remaining sources of the :class:`ParseSource`
    """
    tp = new_token_parser(parse_source.remaining_source)
    yield tp
    parse_source.consume(tp.token_stream.position)


@contextmanager
def from_remaining_part_of_current_line_of_parse_source(parse_source: ParseSource):
    """
    Gives a :class:`TokenParser` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParser` is the remaining part of the current line of the :class:`ParseSource`
    """
    tp = new_token_parser(parse_source.remaining_part_of_current_line)
    yield tp
    parse_source.consume(tp.token_stream.position)
