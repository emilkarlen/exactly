from typing import List, Sequence, Generic, TypeVar

from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parsing import LocationAwareParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo


def remaining_source(remaining_contents_of_first_line: str,
                     following_lines: Sequence[str] = ()) -> TokenParser:
    """
    :param remaining_contents_of_first_line: Part of the first line that has not been consumed.
    :return: Source with some initial content of the first line that has been consumed.
    """
    content = '\n'.join([remaining_contents_of_first_line] + list(following_lines))
    token_stream = TokenStream(content)
    return TokenParser(token_stream)


def remaining_source_lines(lines: List[str]) -> TokenParser:
    """
    A variant of 'remaining_source'.
    """
    if not lines:
        raise ValueError('The source must contain at least one line')
    return remaining_source(lines[0], lines[1:])


T = TypeVar('T')


class ParserAsLocationAwareParser(Generic[T], LocationAwareParser[T]):
    def __init__(self, converted: Parser[T]):
        self.converted = converted

    def parse(self, fs_location_info: FileSystemLocationInfo, source: ParseSource) -> T:
        return self.converted.parse(source)
