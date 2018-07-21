import pathlib
from pathlib import Path
from typing import Sequence, Optional, Callable

from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement, new_empty_element, \
    ParsedFileInclusionDirective, ParsedInstruction
from exactly_lib.section_document.parsing_configuration import SectionElementParser, SectionConfiguration, \
    SectionsConfiguration, FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib_test.section_document.test_resources.element_assertions import InstructionInSection

INCLUDE_DIRECTIVE_NAME = 'include'
OK_INSTRUCTION_NAME = 'ok'
SYNTAX_ERROR_INSTRUCTION_NAME = 'error'
UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE = 'none'
SECTION_1_NAME = 'section1'
SECTION_2_NAME = 'section2'
NO_FILE_INCLUSIONS = []


def inclusion_of_file(file_name) -> str:
    if not isinstance(file_name, str):
        file_name = str(file_name)
    return INCLUDE_DIRECTIVE_NAME + ' ' + file_name


def inclusion_of_list_of_files(files: list) -> str:
    return inclusion_of_file(' '.join(files))


def ok_instruction(arg: str) -> str:
    return OK_INSTRUCTION_NAME + ' ' + arg


def syntax_error_instruction(error_message: str) -> str:
    return SYNTAX_ERROR_INSTRUCTION_NAME + ' ' + error_message


ARBITRARY_OK_INSTRUCTION_SOURCE_LINE = ok_instruction('ok instruction line')


class SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SectionElementParser):
    """
    Parse result:
     - line with only space -> EMPTY element
     - line beginning with SYNTAX_ERROR_INSTRUCTION_NAME -> ParseError
     - line beginning with UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE -> return None
     - OK_INSTRUCTION_NAME -> INSTRUCTION element
    """

    def __init__(self,
                 section_name_to_register_in_instructions: str,
                 extra_inclusion_action: Optional[Callable[[FileSystemLocationInfo, Sequence[Path]], None]] = None
                 ):
        self._section_name_to_register_in_instructions = section_name_to_register_in_instructions
        self.extra_inclusion_action = extra_inclusion_action

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        current_line = source.current_line_text
        if current_line == UNRECOGNIZED_ELEMENT_THAT_CAUSES_RETURN_VALUE_OF_NONE:
            return None
        consumed_source = consume_current_line_and_return_it_as_line_sequence(source)
        if current_line.isspace():
            return new_empty_element(consumed_source)
        current_line_parts = current_line.split()
        if current_line_parts[0] == INCLUDE_DIRECTIVE_NAME:
            paths_to_include = [
                pathlib.Path(file_name)
                for file_name in current_line_parts[1:]
            ]
            if self.extra_inclusion_action is not None:
                self.extra_inclusion_action(fs_location_info, paths_to_include)
            return ParsedFileInclusionDirective(consumed_source, paths_to_include)
        elif current_line_parts[0] == SYNTAX_ERROR_INSTRUCTION_NAME:
            raise SourceError(consumed_source, current_line_parts[1])
        elif current_line_parts[0] == OK_INSTRUCTION_NAME:
            return ParsedInstruction(consumed_source,
                                     InstructionInfo(InstructionInSection(
                                         self._section_name_to_register_in_instructions)))
        else:
            raise ValueError('Unknown source: ' + current_line)


SECTIONS_CONFIGURATION = SectionsConfiguration([
    SectionConfiguration(SECTION_1_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_1_NAME)
                         ),
    SectionConfiguration(SECTION_2_NAME,
                         SectionElementParserForInclusionDirectiveAndOkAndInvalidInstructions(SECTION_2_NAME)
                         ),
])


def consume_current_line_and_return_it_as_line_sequence(source: ParseSource) -> line_source.LineSequence:
    ret_val = line_source.LineSequence(source.current_line_number,
                                       (source.current_line_text,))
    source.consume_current_line()
    return ret_val
