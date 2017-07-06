from exactly_lib.section_document import model
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    InvalidInstructionSyntaxException, UnknownInstructionException, SingleInstructionInvalidArgumentException, \
    InvalidInstructionArgumentException, ArgumentParsingImplementationException
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.util import line_source


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 instruction_name_extractor_function,
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
        self._name_and_argument_splitter = instruction_name_extractor_function

    def parse(self, source: ParseSource) -> model.Instruction:
        first_line = source.current_line
        name = self._extract_name(source)
        parser = self._lookup_parser(first_line, name)
        source.consume_initial_space_on_current_line()
        return self._parse(source, parser, name)

    def _extract_name(self, source: ParseSource) -> str:
        try:
            name = self._name_and_argument_splitter(source.remaining_part_of_current_line)
            source.consume_part_of_current_line(len(name))
        except:
            raise InvalidInstructionSyntaxException(source.current_line)
        return name

    def _lookup_parser(self,
                       original_source_line: line_source.Line,
                       name: str) -> InstructionParser:
        """
        :raises: InvalidInstructionException
        """
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(original_source_line,
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
            raise InvalidInstructionArgumentException(first_line,
                                                      name,
                                                      ex.error_message)
        except Exception as ex:
            raise ArgumentParsingImplementationException(first_line,
                                                         name,
                                                         parser,
                                                         str(ex))
