from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.section_element_parsing import UnrecognizedSectionElementSourceError, \
    RecognizedSectionElementSourceError
from exactly_lib.util import line_source


class SingleInstructionInvalidArgumentException(Exception):
    """
    Indicates invalid arguments to an instruction,
    without the need to specify source code, since it
    can be handled by the code catching the exception.
    """

    def __init__(self, error_message: str):
        self.error_message = error_message


class InvalidInstructionSyntaxException(UnrecognizedSectionElementSourceError):
    """
    The source line is not valid for an instruction.
    """

    def __init__(self,
                 source: line_source.LineSequence,
                 error_message: str = 'Invalid instruction syntax'):
        super().__init__(source,
                         error_message)


class UnknownInstructionException(UnrecognizedSectionElementSourceError):
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


class InvalidInstructionArgumentException(RecognizedSectionElementSourceError):
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


class ArgumentParsingImplementationException(RecognizedSectionElementSourceError):
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
