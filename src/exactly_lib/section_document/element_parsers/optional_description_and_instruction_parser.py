from typing import Optional

from exactly_lib.section_document import syntax, defs
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParser, InstructionAndDescriptionParser, parse_and_compute_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedInstruction
from exactly_lib.section_document.section_element_parsing import new_unrecognized_section_element_error_of_single_line, \
    new_recognized_section_element_error_of_single_line
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util.line_source import Line

_ERR_MSG__MISSING_INSTRUCTION_AFTER_DESCRIPTION = (
    '{EOF} reached without finding {i:a} (following {id:a}).'.format(
        EOF=defs.END_OF_FILE,
        i=defs.INSTRUCTION,
        id=defs.INSTRUCTION_DESCRIPTION,
    )
)
_ERR_MSG__MISSING_END_DELIMITER = (
    'Invalid {id}: end delimiter ({d}) not found.'.format(
        id=defs.INSTRUCTION_DESCRIPTION,
        d=defs.DESCRIPTION_DELIMITER,
    ))


class InstructionWithOptionalDescriptionParser(InstructionAndDescriptionParser):
    def __init__(self, instruction_parser: InstructionParser):
        self.instruction_parser = instruction_parser

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedInstruction:
        first_line = source.current_line
        source_copy = source.copy
        description = _DescriptionExtractor(source_copy).apply()
        self._consume_space_and_comment_lines(source_copy, first_line)
        ret_val = parse_and_compute_source(self.instruction_parser,
                                           fs_location_info,
                                           source_copy,
                                           description)
        source.catch_up_with(source_copy)
        return ret_val

    @staticmethod
    def _consume_space_and_comment_lines(source: ParseSource, first_line: Line):
        if source.is_at_eof:
            raise new_unrecognized_section_element_error_of_single_line(
                first_line,
                _ERR_MSG__MISSING_INSTRUCTION_AFTER_DESCRIPTION,
            )
        line_in_error_message = first_line
        source.consume_initial_space_on_current_line()
        if not source.is_at_eol:
            return
        source.consume_current_line()
        while not source.is_at_eof:
            if syntax.is_empty_or_comment_line(source.current_line_text):
                line_in_error_message = source.current_line
                source.consume_current_line()
            else:
                source.consume_initial_space_on_current_line()
                return
        raise new_unrecognized_section_element_error_of_single_line(line_in_error_message,
                                                                    _ERR_MSG__MISSING_INSTRUCTION_AFTER_DESCRIPTION)


class _DescriptionExtractor:
    def __init__(self, source: ParseSource):
        self.source = source
        self.source.consume_initial_space_on_current_line()
        self.remaining_source = self.source.remaining_source

    def apply(self) -> Optional[str]:
        return (
            self.extract_and_consume_description()
            if self.starts_with_description()
            else
            None
        )

    def extract_and_consume_description(self) -> str:
        end_delimiter_pos = self.remaining_source.find(defs.DESCRIPTION_DELIMITER, 1)
        if end_delimiter_pos == -1:
            raise new_recognized_section_element_error_of_single_line(
                self.source.current_line,
                _ERR_MSG__MISSING_END_DELIMITER)
        description = self.remaining_source[1:end_delimiter_pos]
        self.source.consume(end_delimiter_pos + 1)
        return description.strip()

    def starts_with_description(self) -> bool:
        return self.remaining_source[0] == defs.DESCRIPTION_DELIMITER
