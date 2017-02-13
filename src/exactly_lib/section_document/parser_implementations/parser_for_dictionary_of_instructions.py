from exactly_lib.section_document import model
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    InvalidInstructionSyntaxException, UnknownInstructionException, SingleInstructionInvalidArgumentException, \
    InvalidInstructionArgumentException, ArgumentParsingImplementationException
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser
from exactly_lib.util import line_source


class SingleInstructionParserSource2(tuple):
    def __new__(cls,
                source: ParseSource,
                instruction_argument: str):
        return tuple.__new__(cls, (source, instruction_argument))

    @property
    def source(self) -> ParseSource:
        return self[0]

    @property
    def instruction_argument(self) -> str:
        return self[1]


class NamedInstructionParser:
    """
    Base class for parsers that parse a single instruction.

    Sub class this class for each instruction.

    The name of the instruction has already been parsed.
    And that name has been mapped to this parser.

    This parser is responsible for parsing the arguments of the instruction:
    instruction-arguments = everything that follows the instruction-name.
    It is allowed to consume arbitrary number of lines that it detects as part
    of the instruction.
    """

    def apply(self, source: SingleInstructionParserSource2) -> Instruction:
        """
        The parser must consume the contents of the ParseSource that it parses.
        This is important to remember, since it is possible to read input from
        the ParseSource (the current line) without consuming it.

        :raises SingleInstructionInvalidArgumentException The arguments are invalid.

        :param source: "Located" at the first non-space character following the instruction name on the
        same line as the instruction name; or is at End Of Line if no non-space character follows.

        :return: An instruction, iff the arguments are valid.
        """
        raise NotImplementedError()


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_name__2__single_instruction_parser: dict):
        """
        :param split_line_into_name_and_argument_function Callable that splits a source line text into a
        (name, argument) tuple. The source line text is assumed to contain at least
        an instruction name.
        :param instruction_name__2__single_instruction_parser: dict: str -> NamedInstructionParser
        """
        self.__instruction_name__2__single_instruction_parser = instruction_name__2__single_instruction_parser
        for value in self.__instruction_name__2__single_instruction_parser.values():
            assert isinstance(value, NamedInstructionParser)
        self._name_and_argument_splitter = split_line_into_name_and_argument_function

    def parse(self, source: ParseSource) -> model.Instruction:
        first_line = source.current_line
        name = self._extract_name(source)
        parser = self._lookup_parser(first_line, name)
        source.consume_initial_space_on_current_line()
        return self._parse(SingleInstructionParserSource2(source, source.remaining_part_of_current_line),
                           parser,
                           name)

    def _extract_name(self, source: ParseSource) -> str:
        try:
            name = self._name_and_argument_splitter(source.current_line_text)
            source.consume_part_of_current_line(len(name))
        except:
            raise InvalidInstructionSyntaxException(source.current_line)
        return name

    def _lookup_parser(self,
                       original_source_line: line_source.Line,
                       name: str) -> NamedInstructionParser:
        """
        :raises: InvalidInstructionException
        """
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(original_source_line,
                                              name)
        return self.__instruction_name__2__single_instruction_parser[name]

    @staticmethod
    def _parse(source: SingleInstructionParserSource2,
               parser: NamedInstructionParser,
               name: str) -> Instruction:
        """
        :raises: InvalidInstructionException
        """
        first_line = source.source.current_line
        try:
            return parser.apply(source)
        except SingleInstructionInvalidArgumentException as ex:
            raise InvalidInstructionArgumentException(first_line,
                                                      name,
                                                      ex.error_message)
        except Exception:
            raise ArgumentParsingImplementationException(first_line,
                                                         name,
                                                         parser)  # TODO Change expected type in ex when done replacing
