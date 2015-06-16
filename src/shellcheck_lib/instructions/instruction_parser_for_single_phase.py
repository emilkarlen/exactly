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


class InstructionParserForDictionaryOfInstructions(InstructionParser):
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_name__2__single_instruction_parser: dict):
        """
        :param split_line_into_name_and_argument_function Callable that splits a source line text into a
        (name, argument) tuple. The source line text is assumed to contain at least
        an instruction name.
        :param instruction_name__2__single_instruction_parser: dict: str -> SingleInstructionParser
        """
        self.__instruction_name__2__single_instruction_parser = instruction_name__2__single_instruction_parser
        for value in self.__instruction_name__2__single_instruction_parser.values():
            assert isinstance(value, SingleInstructionParser)
        self._name_and_argument_splitter = split_line_into_name_and_argument_function

    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        """
        :raises: InvalidInstructionException
        """
        (name, argument) = self._name_and_argument_splitter(source_line.text)
        parser = self._lookup_parser(source_line, name)
        instruction = self._parse(source_line, parser, name, argument)
        return model.new_instruction_element(source_line, instruction)

    def _lookup_parser(self,
                       original_source_line: line_source.Line,
                       name: str) -> SingleInstructionParser:
        """
        :raises: InvalidInstructionException
        """
        if name not in self.__instruction_name__2__single_instruction_parser:
            raise UnknownInstructionException(original_source_line,
                                              name)
        return self.__instruction_name__2__single_instruction_parser[name]

    @staticmethod
    def _parse(original_source_line: line_source.Line,
               parser: SingleInstructionParser,
               name: str,
               argument: str) -> Instruction:
        """
        :raises: InvalidInstructionException
        """
        try:
            return parser.apply(argument)
        except SingleInstructionInvalidArgumentException as ex:
            raise InvalidInstructionArgumentException(original_source_line,
                                                      name,
                                                      ex.error_message)
        except Exception:
            raise ArgumentParsingImplementationException(original_source_line,
                                                         name,
                                                         parser)
