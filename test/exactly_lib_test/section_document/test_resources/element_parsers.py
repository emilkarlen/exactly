import pathlib
from typing import Optional

from exactly_lib.section_document import parsing_configuration
from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement
from exactly_lib.section_document.parsing_configuration import SectionElementParser
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import \
    consume_current_line_and_return_it_as_line_sequence


class SectionElementParserThatReturnsNone(SectionElementParser):
    def parse(self,
              file_reference_relativity_root_dir: pathlib.Path,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        return None


class SectionElementParserThatRaisesSourceError(parsing_configuration.SectionElementParser):
    def parse(self,
              file_reference_relativity_root_dir: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        raise SourceError(consume_current_line_and_return_it_as_line_sequence(source),
                          'Unconditional failure')


class SectionElementParserThatReturnsConstantAndConsumesCurrentLine(
    parsing_configuration.SectionElementParser):
    def __init__(self, return_value: ParsedSectionElement):
        self.return_value = return_value

    def parse(self,
              file_reference_relativity_root_dir: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        source.consume_current_line()
        return self.return_value
