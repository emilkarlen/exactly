from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.parse_source import ParseSource


@contextmanager
def token_stream_from_parse_source(parse_source: ParseSource) -> ContextManager[TokenStream]:
    """
    Gives a :class:`TokenStream` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenStream` is the remaining sources of the :class:`ParseSource`
    """
    ts = new_token_stream(parse_source.remaining_source)
    yield ts
    parse_source.consume(ts.position)


@contextmanager
def token_stream_from_remaining_part_of_current_line_of_parse_source(parse_source: ParseSource
                                                                     ) -> ContextManager[TokenStream]:
    """
    Gives a :class:`TokenStream` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenStream` is the remaining part of the current line of the :class:`ParseSource`
    """
    ts = new_token_stream(parse_source.remaining_part_of_current_line)
    yield ts
    parse_source.consume(ts.position)
