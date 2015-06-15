from shellcheck_lib.document import model
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parse import InstructionParser
from shellcheck_lib.general import line_source


class SingleInstructionInvalidArgumentException(Exception):
    """
    Indicates invalid arguments to an instruction.
    """

    def __init__(self,
                 error_message: str):
        self.error_message = error_message


class SingleInstructionParser:
    """
    Base class for parsers that parse a single instruction.

    Sub class this class for each instruction.

    The name of the instruction has already been parsed.
    And that name has been mapped to this parser.

    This parser is responsible for parsing the arguments of the instruction:
    instruction-arguments = everything that follows the instruction-name.
    """

    def apply(self,
              instruction_argument: str) -> Instruction:
        """
        The name of the instruction has already been parsed.
        And that name has been mapped to this parser.

        :raises SingleInstructionInvalidArgumentException The arguments are invalid.

        :param instruction_argument: The string that follows the instruction-name.
        Can include new-lines.
        :return: An instruction, iff the arguments are valid.
        """
        raise NotImplementedError()


class InvalidInstructionException(Exception):
    """
    Indicates some kind of invalid instruction.
    """

    def __init__(self,
                 line: line_source.Line):
        self.line = line


class InvalidInstructionSyntaxException(Exception):
    """
    The source line is not valid for an instruction.
    """

    def __init__(self,
                 line: line_source.Line):
        self.line = line


class UnknownInstructionException(InvalidInstructionException):
    """
    Indicates that an unknown instruction has been encountered.

    The name of the instruction is unknown.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str):
        super().__init__(line)
        self.instruction_name = instruction_name


class InvalidInstructionArgumentException(InvalidInstructionException):
    """
    Indicates that an unknown instruction has been encountered.

    The name of the instruction is unknown.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str,
                 error_message: str):
        super().__init__(line)
        self.instruction_name = instruction_name
        self.error_message = error_message


class ArgumentParsingImplementationException(InvalidInstructionException):
    """
    An implementation error was encountered during parsing of the argument
    of an instruction.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str,
                 parser_that_raised_exception: SingleInstructionParser):
        super().__init__(line)
        self.instruction_name = instruction_name
        self.parser_that_raised_exception = parser_that_raised_exception


class _InstructionParserForPhase(InstructionParser):
    def __init__(self,
                 instruction_name__2__single_instruction_parser: dict):
        self.__instruction_name__2__single_instruction_parser = instruction_name__2__single_instruction_parser
        for value in self.__instruction_name__2__single_instruction_parser.values():
            assert isinstance(value, SingleInstructionParser)

    # def apply(self, line: line_source.Line) -> model.PhaseContentElement:
    def apply(self, line: line_source.Line) -> Instruction:
        """
        :raises: InvalidInstructionException
        :param line: The source code to parse.
        """
        (name, argument) = self._split_name_and_argument(line.text)
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(line,
                                              name)
        single_instruction_parser = self.__instruction_name__2__single_instruction_parser[name]
        try:
            return single_instruction_parser.apply(argument)
        except SingleInstructionInvalidArgumentException as ex:
            raise InvalidInstructionArgumentException(line,
                                                      name,
                                                      ex.error_message)
        except Exception:
            raise ArgumentParsingImplementationException(line,
                                                         name,
                                                         single_instruction_parser)

    @staticmethod
    def _split_name_and_argument(instruction_source: str) -> tuple:
        # DUMMY DUMMY IMPLEMENTATION - TEST DRIVING!
        return instruction_source[1], instruction_source[1:]


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 instruction_name__2__single_instruction_parser: dict):
        """
        :param instruction_name__2__single_instruction_parser: dict: str -> SingleInstructionParser
        """
        self.parser = _InstructionParserForPhase(instruction_name__2__single_instruction_parser)

    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        """
        :raises: InvalidInstructionException
        """
        instruction = self.parser.apply(source_line)
        return model.new_instruction_element(source_line, instruction)
