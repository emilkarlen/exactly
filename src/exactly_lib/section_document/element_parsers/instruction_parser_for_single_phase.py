from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.exceptions import SourceError
from exactly_lib.util import line_source


class SingleInstructionInvalidArgumentException(Exception):
    """
    Indicates invalid arguments to an instruction.
    """

    def __init__(self,
                 error_message: str):
        self.error_message = error_message


class InvalidInstructionException(SourceError):
    """
    Indicates some kind of invalid instruction.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 message: str):
        super().__init__(source, message)


class InvalidInstructionSyntaxException(InvalidInstructionException):
    """
    The source line is not valid for an instruction.
    """

    def __init__(self,
                 source: line_source.LineSequence):
        super().__init__(source,
                         'Invalid instruction syntax')


class UnknownInstructionException(InvalidInstructionException):
    """
    Indicates that an unknown instruction has been encountered.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 instruction_name: str):
        super().__init__(source,
                         'Unknown instruction: ' + instruction_name)
        self._instruction_name = instruction_name

    @property
    def instruction_name(self) -> str:
        return self._instruction_name


class InvalidInstructionArgumentException(InvalidInstructionException):
    """
    Indicates that an unknown instruction argument has been encountered.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 instruction_name: str,
                 error_message: str):
        super().__init__(source,
                         'Invalid argument for %s:\n%s' % (instruction_name, error_message))
        self.instruction_name = instruction_name
        self.error_message = error_message


class ArgumentParsingImplementationException(SourceError):
    """
    An implementation error was encountered during parsing of the argument
    of an instruction.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 instruction_name: str,
                 parser_that_raised_exception: InstructionParser,
                 msg: str):
        super().__init__(source, msg)
        self.instruction_name = instruction_name
        self.parser_that_raised_exception = parser_that_raised_exception
