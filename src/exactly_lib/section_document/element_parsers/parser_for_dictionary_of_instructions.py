from typing import Callable, Dict

from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    InvalidInstructionSyntaxException, UnknownInstructionException, SingleInstructionInvalidArgumentException, \
    InvalidInstructionArgumentException, ArgumentParsingImplementationException
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util import line_source
from exactly_lib.util.line_source import line_sequence_from_line, LineSequence

InstructionNameExtractor = Callable[[str], str]


class _ErrMsgSourceConstructor:
    def __init__(self, before_parse: ParseSource):
        self._first_line = before_parse.current_line
        self._remaining__before = before_parse.remaining_source

    def ending_at(self, after_parse: ParseSource) -> LineSequence:
        num_chars = len(self._remaining__before) - len(after_parse.remaining_source)

        if num_chars < len(self._first_line.text):
            return line_sequence_from_line(self._first_line)

        source__consumed = self._remaining__before[:num_chars].rstrip()
        return LineSequence(self._first_line.line_number, source__consumed.split('\n'))


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 instruction_name_extractor_function: InstructionNameExtractor,
                 instruction_name__2__single_instruction_parser: Dict[str, InstructionParser]):
        """
        :param instruction_name_extractor_function Callable that extracts an instruction name from a source line.
        The source line text is assumed to contain at least
        an instruction name.
        """
        self.__instruction_name__2__single_instruction_parser = instruction_name__2__single_instruction_parser
        for value in self.__instruction_name__2__single_instruction_parser.values():
            assert isinstance(value, InstructionParser)
        self._instruction_name_extractor_function = instruction_name_extractor_function

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> model.Instruction:
        err_msg_constructor = _ErrMsgSourceConstructor(source)
        name = self._extract_name(source)
        parser = self._lookup_parser(source.current_line, name)
        source.consume_part_of_current_line(len(name))
        source.consume_initial_space_on_current_line()
        return self._parse(fs_location_info, source, parser, name, err_msg_constructor)

    def _extract_name(self, source: ParseSource) -> str:
        try:
            name = self._instruction_name_extractor_function(source.remaining_part_of_current_line)
            if not isinstance(name, str):
                raise InvalidInstructionSyntaxException(line_sequence_from_line(source.current_line))
        except Exception:
            raise InvalidInstructionSyntaxException(line_sequence_from_line(source.current_line))
        return name

    def _lookup_parser(self,
                       original_source_line: line_source.Line,
                       name: str) -> InstructionParser:
        """
        :raises: UnknownInstructionException
        """
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(line_sequence_from_line(original_source_line),
                                              name)
        return self.__instruction_name__2__single_instruction_parser[name]

    @staticmethod
    def _parse(fs_location_info: FileSystemLocationInfo,
               source: ParseSource,
               parser: InstructionParser,
               name: str,
               err_msg_src_constructor: _ErrMsgSourceConstructor,
               ) -> model.Instruction:
        """
        :raises: InvalidInstructionException
        """
        try:
            return parser.parse(fs_location_info, source)
        except SingleInstructionInvalidArgumentException as ex:

            raise InvalidInstructionArgumentException(err_msg_src_constructor.ending_at(source),
                                                      name,
                                                      ex.error_message)
        except Exception as ex:
            raise ArgumentParsingImplementationException(err_msg_src_constructor.ending_at(source),
                                                         name,
                                                         parser,
                                                         str(ex))
