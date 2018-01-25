from typing import Callable

from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    InvalidInstructionSyntaxException, UnknownInstructionException, SingleInstructionInvalidArgumentException, \
    InvalidInstructionArgumentException, ArgumentParsingImplementationException
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util import line_source
from exactly_lib.util.line_source import line_sequence_from_line

InstructionNameExtractor = Callable[[str], str]


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 instruction_name_extractor_function: InstructionNameExtractor,
                 instruction_name__2__single_instruction_parser: dict):
        """
        :param instruction_name_extractor_function Callable that extracts an instruction name from a source line.
        The source line text is assumed to contain at least
        an instruction name.
        :param instruction_name__2__single_instruction_parser: dict: str -> SingleTypeOfInstructionParser
        """
        self.__instruction_name__2__single_instruction_parser = instruction_name__2__single_instruction_parser
        for value in self.__instruction_name__2__single_instruction_parser.values():
            assert isinstance(value, InstructionParser)
        self._instruction_name_extractor_function = instruction_name_extractor_function

    def parse(self, source: ParseSource) -> model.Instruction:
        first_line = source.current_line
        name = self._extract_name(source)
        parser = self._lookup_parser(first_line, name)
        source.consume_initial_space_on_current_line()
        return self._parse(source, parser, name)

    def _extract_name(self, source: ParseSource) -> str:
        try:
            name = self._instruction_name_extractor_function(source.remaining_part_of_current_line)
            source.consume_part_of_current_line(len(name))
        except Exception:
            raise InvalidInstructionSyntaxException(line_sequence_from_line(source.current_line))
        return name

    def _lookup_parser(self,
                       original_source_line: line_source.Line,
                       name: str) -> InstructionParser:
        """
        :raises: InvalidInstructionException
        """
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(line_sequence_from_line(original_source_line),
                                              name)
        return self.__instruction_name__2__single_instruction_parser[name]

    @staticmethod
    def _parse(source: ParseSource,
               parser: InstructionParser,
               name: str) -> model.Instruction:
        """
        :raises: InvalidInstructionException
        """
        first_line = source.current_line
        try:
            return parser.parse(source)
        except SingleInstructionInvalidArgumentException as ex:
            raise InvalidInstructionArgumentException(line_sequence_from_line(first_line),
                                                      name,
                                                      ex.error_message)
        except Exception as ex:
            raise ArgumentParsingImplementationException(line_sequence_from_line(first_line),
                                                         name,
                                                         parser,
                                                         str(ex))
