from typing import Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib.section_document.section_element_parsing import SectionElementParser, \
    RecognizedSectionElementSourceError
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import \
    consume_current_line_and_return_it_as_line_sequence


class SectionElementParserThatReturnsNone(SectionElementParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        return None


class SectionElementParserThatRaisesRecognizedSectionElementSourceError(SectionElementParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedSectionElement:
        raise RecognizedSectionElementSourceError(consume_current_line_and_return_it_as_line_sequence(source),
                                                  'Unconditional failure')


class SectionElementParserThatReturnsConstantAndConsumesCurrentLine(SectionElementParser):
    def __init__(self, return_value: ParsedSectionElement):
        self.return_value = return_value

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedSectionElement:
        source.consume_current_line()
        return self.return_value
