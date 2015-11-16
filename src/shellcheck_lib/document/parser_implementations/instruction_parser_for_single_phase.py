from shellcheck_lib.document import model
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document import parse
from shellcheck_lib.document import syntax
from shellcheck_lib.document.parse import SourceError
from shellcheck_lib.general import line_source


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


class SectionElementParserForStandardCommentAndEmptyLines(parse.SectionElementParser):
    def apply(self, source: line_source.LineSequenceBuilder) -> model.PhaseContentElement:
        first_line = source.first_line
        if syntax.is_empty_line(first_line.text):
            return model.new_empty_e(source.build())
        if syntax.is_comment_line(first_line.text):
            return model.new_comment_e(source.build())
        instruction = self._parse_instruction(source)
        return model.new_instruction_e(source.build(), instruction)

    def _parse_instruction(self,
                           source: line_source.LineSequenceBuilder) -> Instruction:
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
                 parser_that_raised_exception: SingleInstructionParser):
        super().__init__(line,
                         'Parser implementation error while parsing ' + instruction_name)
        self.instruction_name = instruction_name
        self.parser_that_raised_exception = parser_that_raised_exception


class SectionElementParserForDictionaryOfInstructions(SectionElementParserForStandardCommentAndEmptyLines):
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

    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> Instruction:
        first_line = source.first_line
        (name, argument) = self._split(first_line)
        parser = self._lookup_parser(first_line, name)
        return self._parse(SingleInstructionParserSource(source, argument),
                           parser,
                           name)

    def _split(self, source_line: line_source.Line) -> (str, str):
        try:
            (name, arg) = self._name_and_argument_splitter(source_line.text)
            return name, arg
        except:
            raise InvalidInstructionSyntaxException(source_line)

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
    def _parse(source: SingleInstructionParserSource,
               parser: SingleInstructionParser,
               name: str) -> Instruction:
        """
        :raises: InvalidInstructionException
        """
        try:
            return parser.apply(source)
        except SingleInstructionInvalidArgumentException as ex:
            raise InvalidInstructionArgumentException(source.line_sequence.first_line,
                                                      name,
                                                      ex.error_message)
        except Exception:
            raise ArgumentParsingImplementationException(source.line_sequence.first_line,
                                                         name,
                                                         parser)
