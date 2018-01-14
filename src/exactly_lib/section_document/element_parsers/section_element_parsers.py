import pathlib
from typing import Sequence

from exactly_lib.section_document import model
from exactly_lib.section_document import syntax
from exactly_lib.section_document.document_parser import SectionElementParser
from exactly_lib.section_document.model import InstructionInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_element_parser import ParsedSectionElement, new_empty_element, \
    new_comment_element, ParsedInstruction
from exactly_lib.util import line_source


class InstructionAndDescriptionParser(SectionElementParser):
    """
    Parses an instruction, optionally preceded by an description.

    Raises an exception if the parse fails.
    """

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedInstruction:
        """
        :raises FileSourceError The description or instruction cannot be parsed.
        """
        raise NotImplementedError()


class InstructionParser:
    """
    Parses a single instruction.

    Raises an exception if the parse fails.
    """

    def parse(self, source: ParseSource) -> model.Instruction:
        """
        :raises FileSourceError The instruction cannot be parsed.
        """
        raise NotImplementedError()


class InstructionWithoutDescriptionParser(InstructionAndDescriptionParser):
    def __init__(self, instruction_parser: InstructionParser):
        self.instruction_parser = instruction_parser

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedInstruction:
        return parse_and_compute_source(self.instruction_parser, source)


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
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        for parser in self._parsers_to_try:
            element = parser.parse(file_inclusion_relativity_root, source)
            if element is not None:
                return element
        return None


class StandardSyntaxElementParser(SectionElementParser):
    """
    A parser that knows how to parse empty lines and
    comment lines (denoted by standard syntax).
    Every other line is treated as the start of a directive or
    an instruction to be parsed by a given instruction parser.
    """

    def __init__(self, instruction_or_directive_parser: SectionElementParser):
        self.instruction_or_directive_parser = instruction_or_directive_parser

    def parse(self,
              file_inclusion_relativity_root: pathlib.Path,
              source: ParseSource) -> ParsedSectionElement:
        first_line = source.current_line
        if syntax.is_empty_line(first_line.text):
            return new_empty_element(self._consume_and_return_current_line(source))
        if syntax.is_comment_line(first_line.text):
            return new_comment_element(self._consume_and_return_current_line(source))
        else:
            return self.instruction_or_directive_parser.parse(file_inclusion_relativity_root,
                                                              source)

    @staticmethod
    def _consume_and_return_current_line(source: ParseSource) -> line_source.LineSequence:
        current_line = source.current_line
        source.consume_current_line()
        return line_source.LineSequence(current_line.line_number,
                                        (current_line.text,))


def parse_and_compute_source(parser: InstructionParser,
                             source: ParseSource,
                             description: str = None) -> ParsedInstruction:
    source_before = source.remaining_source
    first_line_number = source.current_line_number
    len_before_parse = len(source_before)
    instruction = parser.parse(source)
    len_after_parse = len(source.remaining_source)
    len_instruction_source = len_before_parse - len_after_parse
    instruction_source = source_before[:len_instruction_source]
    source = line_source.LineSequence(first_line_number, tuple(instruction_source.split('\n')))
    return ParsedInstruction(source,
                             InstructionInfo(instruction,
                                             description))
