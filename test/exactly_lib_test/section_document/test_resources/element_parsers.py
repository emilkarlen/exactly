import pathlib

from exactly_lib.section_document import document_parser as sut
from exactly_lib.section_document.document_parser import SectionElementParser
from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import \
    consume_current_line_and_return_it_as_line_sequence


class SectionElementParserThatReturnsNone(SectionElementParser):
    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        return None


class SectionElementParserThatRaisesSourceError(sut.SectionElementParser):
    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        raise SourceError(consume_current_line_and_return_it_as_line_sequence(source),
                          'Unconditional failure')


class SectionElementParserThatReturnsConstantAndConsumesCurrentLine(sut.SectionElementParser):
    def __init__(self, return_value: ParsedSectionElement):
        self.return_value = return_value

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        source.consume_current_line()
        return self.return_value
