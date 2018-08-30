from exactly_lib.section_document.document_parser import DocumentParser
from exactly_lib.section_document.document_parsers import new_parser_for
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement, new_empty_element, \
    new_comment_element, ParsedInstruction
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.section_document.section_parsing import SectionsConfiguration, \
    SectionConfiguration
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib_test.section_document.document_parser.test_resources.element_parser import \
    consume_current_line_and_return_it_as_line_sequence
from exactly_lib_test.section_document.test_resources.element_assertions import InstructionInSection
from exactly_lib_test.section_document.test_resources.element_parsers import \
    SectionElementParserThatRaisesRecognizedSectionElementSourceError

_COMMENT_START = 'COMMENT'
_MULTI_LINE_INSTRUCTION_LINE_START = 'MULTI-LINE-INSTRUCTION'


def is_multi_line_instruction_line(line: str) -> bool:
    return line[:len(_MULTI_LINE_INSTRUCTION_LINE_START)] == _MULTI_LINE_INSTRUCTION_LINE_START


def is_comment_line(line: str) -> bool:
    return line[:len(_COMMENT_START)] == _COMMENT_START


class SectionElementParserForEmptyCommentAndInstructionLines(SectionElementParser):
    def __init__(self, section_name: str):
        self._section_name = section_name

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedSectionElement:
        current_line = source.current_line_text
        if current_line == '':
            return new_empty_element(consume_current_line_and_return_it_as_line_sequence(source))
        elif is_comment_line(current_line):
            return new_comment_element(consume_current_line_and_return_it_as_line_sequence(source))

        else:
            instruction_source = self._consume_instruction_source(source)
            return ParsedInstruction(instruction_source,
                                     InstructionInfo(InstructionInSection(self._section_name)))

    @staticmethod
    def _consume_instruction_source(source: ParseSource) -> line_source.LineSequence:
        current_line = source.current_line_text
        if is_multi_line_instruction_line(current_line):
            first_line_number = source.current_line_number
            lines = [current_line]
            source.consume_current_line()
            # Eat additional lines
            while source.has_current_line:
                current_line = source.current_line_text
                if is_multi_line_instruction_line(current_line):
                    lines.append(current_line)
                    source.consume_current_line()
                else:
                    break
            return line_source.LineSequence(first_line_number, tuple(lines))
        else:
            return consume_current_line_and_return_it_as_line_sequence(source)


def parser_for_section2_that_fails_unconditionally() -> DocumentParser:
    return parser_with_successful_and_failing_section_parsers('section 1', 'section 2')


def parser_with_successful_and_failing_section_parsers(successful_section: str,
                                                       failing_section: str,
                                                       default_section: str = None) -> DocumentParser:
    configuration = SectionsConfiguration(
        (SectionConfiguration(successful_section,
                              SectionElementParserForEmptyCommentAndInstructionLines(
                                  successful_section)),
         SectionConfiguration(failing_section,
                              SectionElementParserThatRaisesRecognizedSectionElementSourceError())),
        default_section_name=default_section)

    return new_parser_for(configuration)


def parser_for_sections(section_names: list,
                        default_section_name: str = None) -> DocumentParser:
    sections = [SectionConfiguration(name,
                                     SectionElementParserForEmptyCommentAndInstructionLines(name))
                for name in section_names]
    if default_section_name is not None:
        if default_section_name not in section_names:
            raise ValueError('Test setup: The given default section %s is not the name of a section (%s)' % (
                default_section_name,
                section_names,
            ))
    configuration = SectionsConfiguration(
        tuple(sections),
        default_section_name=default_section_name)
    return new_parser_for(configuration)
