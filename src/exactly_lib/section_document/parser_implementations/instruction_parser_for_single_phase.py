from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parser_implementations.new_section_element_parser import InstructionParser
from exactly_lib.util import line_source


class SingleInstructionInvalidArgumentException(Exception):
    """
    Indicates invalid arguments to an instruction.
    """

    def __init__(self,
                 error_message: str):
        self.error_message = error_message


class SingleInstructionParserSource(tuple):
    def __new__(cls,
                line_sequence: line_source.LineSequenceBuilder,
                instruction_argument: str):
        return tuple.__new__(cls, (line_sequence, instruction_argument))

    @property
    def line_sequence(self) -> line_source.LineSequenceBuilder:
        return self[0]

    @property
    def instruction_argument(self) -> str:
        return self[1]


class SingleInstructionParser:
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

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        """
        The name of the instruction has already been parsed.
        And that name has been mapped to this parser.

        :raises SingleInstructionInvalidArgumentException The arguments are invalid.

        :param source: First line is the line with the instruction name at the
        beginning, followed by the instruction_argument.
        This, and only this, first line has been consumed.

        :return: An instruction, iff the arguments are valid.
        """
        raise NotImplementedError()


class InvalidInstructionException(SourceError):
    """
    Indicates some kind of invalid instruction.
    """

    def __init__(self,
                 line: line_source.Line,
                 message: str):
        super().__init__(line, message)


class InvalidInstructionSyntaxException(InvalidInstructionException):
    """
    The source line is not valid for an instruction.
    """

    def __init__(self,
                 line: line_source.Line):
        super().__init__(line, 'Invalid instruction syntax')


class UnknownInstructionException(InvalidInstructionException):
    """
    Indicates that an unknown instruction has been encountered.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str):
        super().__init__(line,
                         'Unknown instruction: ' + instruction_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name


class InvalidInstructionArgumentException(InvalidInstructionException):
    """
    Indicates that an unknown instruction has been encountered.

    The name of the instruction is unknown.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str,
                 error_message: str):
        super().__init__(line,
                         'Invalid argument for %s:\n%s' % (instruction_name, error_message))
        self.instruction_name = instruction_name
        self.error_message = error_message


class ArgumentParsingImplementationException(SourceError):
    """
    An implementation error was encountered during parsing of the argument
    of an instruction.
    """

    def __init__(self,
                 line: line_source.Line,
                 instruction_name: str,
                 parser_that_raised_exception: InstructionParser):
        super().__init__(line,
                         'Parser implementation error while parsing ' + instruction_name)
        self.instruction_name = instruction_name
        self.parser_that_raised_exception = parser_that_raised_exception
