from abc import ABC, abstractmethod
from typing import Sequence, Callable, Optional

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parsed_section_element import ParsedSectionElement, new_empty_element, \
    new_comment_element, ParsedInstruction, ParsedNonInstructionElement
from exactly_lib.section_document.section_element_parsing import SectionElementParser, \
    UnrecognizedSectionElementSourceError, LocationAwareParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source


class InstructionAndDescriptionParser(SectionElementParser):
    """
    Parses an instruction, optionally preceded by an description.

    Raises an exception if the parse fails.
    """

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedInstruction:
        """
        :raises FileSourceError The description or instruction cannot be parsed.
        """
        raise NotImplementedError()


class InstructionParser(LocationAwareParser[model.Instruction], ABC):
    """
    Parses a single instruction.

    Raises an exception if the parse fails.
    """

    @abstractmethod
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        """
        :raises FileSourceError The instruction cannot be parsed.
        """
        pass


class InstructionParserWithoutSourceFileLocationInfo(InstructionParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        return self.parse_from_source(source)

    def parse_from_source(self, source: ParseSource) -> model.Instruction:
        """
        :raises FileSourceError The instruction cannot be parsed.
        """
        raise NotImplementedError()


class InstructionWithoutDescriptionParser(InstructionAndDescriptionParser):
    def __init__(self, instruction_parser: InstructionParser):
        self.instruction_parser = instruction_parser

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> ParsedInstruction:
        return parse_and_compute_source(self.instruction_parser,
                                        fs_location_info,
                                        source)


class ParserFromSequenceOfParsers(SectionElementParser):
    """
    A parser that tries a sequence of parsers, and returns the value
    from the first parser that gives a result that is not None.

    A parser that returns None, must not consume source.

    An exception from a parser will be propagated from this parser.
    """

    def __init__(self, parsers_to_try: Sequence[SectionElementParser]):
        """
        :param parsers_to_try: Parsers to try - in precedence order.
        """
        self._parsers_to_try = parsers_to_try

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedSectionElement]:
        last_error = None

        for parser in self._parsers_to_try:
            try:
                element = parser.parse(fs_location_info, source)
                if element is not None:
                    return element
                else:
                    last_error = None
            except UnrecognizedSectionElementSourceError as ex:
                last_error = ex

        if last_error is not None:
            raise last_error
        return None


class StandardSyntaxCommentAndEmptyLineParser(SectionElementParser):
    """
    Parser for comments and empty lines, according to "standard" syntax.

    (See module syntax for def of standard syntax.)

    Reports/returns None if the current source line is neither a comment
    nor an empty line.
    """

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> Optional[ParsedNonInstructionElement]:
        first_line = source.current_line
        if syntax.is_empty_line(first_line.text):
            return new_empty_element(self._consume_and_return_current_line(source,
                                                                           syntax.is_empty_line))
        if syntax.is_comment_line(first_line.text):
            return new_comment_element(self._consume_and_return_current_line(source,
                                                                             syntax.is_comment_line))
        else:
            return None

    @staticmethod
    def _consume_and_return_current_line(source: ParseSource,
                                         line_predicate_for_line_to_consume: Callable[[str], bool],
                                         ) -> line_source.LineSequence:
        current_line = source.current_line
        lines = [current_line.text]
        source.consume_current_line()

        while source.has_current_line and line_predicate_for_line_to_consume(source.current_line_text):
            lines.append(source.current_line_text)
            source.consume_current_line()

        return line_source.LineSequence(current_line.line_number,
                                        tuple(lines))


def standard_syntax_element_parser(instruction_or_directive_parser: SectionElementParser) -> SectionElementParser:
    """
    A parser that knows how to parse empty lines and
    comment lines (denoted by standard syntax).
    Every other line is treated as the start of a directive or
    an instruction to be parsed by a given instruction parser.
    """
    return ParserFromSequenceOfParsers([
        StandardSyntaxCommentAndEmptyLineParser(),
        instruction_or_directive_parser,
    ])


def parse_and_compute_source(parser: InstructionParser,
                             fs_location_info: FileSystemLocationInfo,
                             source: ParseSource,
                             description: str = None) -> ParsedInstruction:
    source_before = source.remaining_source
    first_line_number = source.current_line_number
    len_before_parse = len(source_before)
    instruction = parser.parse(fs_location_info, source)
    len_after_parse = len(source.remaining_source)
    len_instruction_source = len_before_parse - len_after_parse
    instruction_source = source_before[:len_instruction_source]
    lines = instruction_source.split('\n')
    if len(lines) > 1 and lines[-1] == '':
        del lines[-1]
    source = line_source.LineSequence(first_line_number, tuple(lines))
    return ParsedInstruction(source,
                             InstructionInfo(instruction,
                                             description))
