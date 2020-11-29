import enum
from abc import ABC
from typing import Optional, Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.tcfs.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntax as string_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx


class ProgramAbsStx(AbstractSyntax, ABC):
    pass


class TransformableProgramAbsStx(ProgramAbsStx, ABC):
    pass


class ArgumentAbsStx(AbstractSyntax, ABC):
    pass


class ArgumentOfSymbolReferenceAbsStx(ArgumentAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class ArgumentOfStringAbsStx(ArgumentAbsStx):
    def __init__(self, string: NonHereDocStringAbsStx):
        self.string = string

    @staticmethod
    def of_str(argument: str,
               quoting: Optional[QuoteType] = None,
               ) -> ArgumentAbsStx:
        return ArgumentOfStringAbsStx(string_abs_stx.StringLiteralAbsStx(argument, quoting))

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class ArgumentOfTextUntilEndOfLineAbsStx(ArgumentAbsStx):
    def __init__(self, text_until_end_of_line: NonHereDocStringAbsStx):
        self.text_until_end_of_line = text_until_end_of_line

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
            self.text_until_end_of_line.tokenization()
        ])


class NonSymLinkFileType(enum.Enum):
    REGULAR = 1
    DIRECTORY = 2


class ArgumentOfExistingPathAbsStx(ArgumentAbsStx):
    PATH_OPTIONS = {
        None: syntax_elements.EXISTING_PATH_OPTION_NAME,
        NonSymLinkFileType.REGULAR: syntax_elements.EXISTING_FILE_OPTION_NAME,
        NonSymLinkFileType.DIRECTORY: syntax_elements.EXISTING_DIR_OPTION_NAME,
    }

    def __init__(self,
                 path: PathAbsStx,
                 file_type: Optional[NonSymLinkFileType] = None
                 ):
        self.path = path
        self.file_type = file_type

    def tokenization(self) -> TokenSequence:
        return token_sequences.OptionWMandatoryValue.of_option_name(
            self.PATH_OPTIONS[self.file_type],
            self.path.tokenization(),
        )


class TransformedProgramAbsStx(ProgramAbsStx):
    def __init__(self,
                 transformed: TransformableProgramAbsStx,
                 transformer: StringTransformerAbsStx,
                 ):
        self.transformed = transformed
        self.transformer = transformer

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.transformed.tokenization(),
            TokenSequence.new_line(),
            token_sequences.OptionWMandatoryValue.of_option_name(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                self.transformer.tokenization(),
            ),
        ])


class ProgramOfExecutableFileCommandLineAbsStx(TransformableProgramAbsStx):
    def __init__(self,
                 executable_file: PathAbsStx,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.executable_file = executable_file
        self._arguments = _ArgumentsAbsStx(arguments)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.executable_file.tokenization(),
            self._arguments.tokenization(),
        ])


class ProgramOfSystemCommandLineAbsStx(TransformableProgramAbsStx):
    def __init__(self,
                 system_command: NonHereDocStringAbsStx,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.system_command = system_command
        self._arguments = _ArgumentsAbsStx(arguments)

    @staticmethod
    def of_str(system_command: str,
               arguments: Sequence[ArgumentAbsStx] = (),
               ) -> TransformableProgramAbsStx:
        return ProgramOfSystemCommandLineAbsStx(
            string_abs_stx.StringLiteralAbsStx(system_command),
            arguments,
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SYSTEM_PROGRAM_TOKEN),
            self.system_command.tokenization(),
            self._arguments.tokenization(),
        ])


class ProgramOfPythonInterpreterAbsStx(TransformableProgramAbsStx):
    def __init__(self, arguments: Sequence[ArgumentAbsStx]):
        self._arguments = _ArgumentsAbsStx(arguments)

    @staticmethod
    def of_execute_python_src_string(py_src: str) -> TransformableProgramAbsStx:
        return ProgramOfPythonInterpreterAbsStx([
            ArgumentOfStringAbsStx.of_str(python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE),
            ArgumentOfStringAbsStx.of_str(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
            ArgumentOfStringAbsStx.of_str(py_src),
        ])

    @staticmethod
    def of_execute_python_src_file(py_file: PathAbsStx,
                                   arguments: Sequence[ArgumentAbsStx] = (),
                                   ) -> TransformableProgramAbsStx:
        return ProgramOfPythonInterpreterAbsStx([ArgumentOfExistingPathAbsStx(py_file)] + list(arguments))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            token_sequences.Option.of_option_name(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
            self._arguments.tokenization(),
        ])


class ProgramOfSymbolReferenceAbsStx(TransformableProgramAbsStx):
    def __init__(self,
                 symbol_name: str,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.symbol_name = symbol_name
        self._arguments = _ArgumentsAbsStx(arguments)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SYMBOL_REF_PROGRAM_TOKEN),
            TokenSequence.singleton(self.symbol_name),
            self._arguments.tokenization(),
        ])


class ProgramOfShellCommandLineAbsStx(TransformableProgramAbsStx):
    def __init__(self, command_line: NonHereDocStringAbsStx):
        self.command_line = command_line

    @staticmethod
    def of_plain_string(command_line: str) -> 'ProgramOfShellCommandLineAbsStx':
        return ProgramOfShellCommandLineAbsStx(string_abs_stx.StringLiteralAbsStx(command_line))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SHELL_COMMAND_TOKEN),
            self.command_line.tokenization(),
        ])


class TransformableProgramAbsStxBuilder:
    def __init__(self, untransformed: TransformableProgramAbsStx):
        self._untransformed = untransformed

    def without_transformation(self) -> TransformableProgramAbsStx:
        return self._untransformed

    def with_transformation(self, transformer: StringTransformerAbsStx) -> ProgramAbsStx:
        return TransformedProgramAbsStx(self._untransformed, transformer)

    def with_and_without_transformer_cases(self, transformer: StringTransformerAbsStx,
                                           ) -> Sequence[NameAndValue[ProgramAbsStx]]:
        return [
            NameAndValue('without transformation', self.without_transformation()),
            NameAndValue('with transformation', self.with_transformation(transformer)),
        ]


class _ArgumentsAbsStx(AbstractSyntax):
    def __init__(self, arguments: Sequence[ArgumentAbsStx],
                 ):
        self._arguments = arguments

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            argument.tokenization()
            for argument in self._arguments
        ])


ARBITRARY_TRANSFORMABLE_PROGRAM = ProgramOfSystemCommandLineAbsStx.of_str('system-program')
