from typing import Sequence, Optional

from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionalAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx, PgmAndArgsAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx, \
    ArgumentOfExistingPathAbsStx, ArgumentsAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx


class CustomPgmAndArgsAbsStx(PgmAndArgsAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    def tokenization(self) -> TokenSequence:
        return self._tokens


class PgmAndArgsWArgumentsAbsStx(PgmAndArgsAbsStx):
    def __init__(self,
                 pgm_and_args: PgmAndArgsAbsStx,
                 arguments: Sequence[ArgumentAbsStx],
                 ):
        self._pgm_and_args = pgm_and_args
        self._arguments = arguments

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._pgm_and_args.tokenization(),
            ArgumentsAbsStx(self._arguments).tokenization(),
        ])


class FullProgramAbsStx(ProgramAbsStx):
    def __init__(self,
                 pgm_and_args: PgmAndArgsAbsStx,
                 stdin: Optional[StringSourceAbsStx] = None,
                 transformation: Optional[StringTransformerAbsStx] = None,
                 ):
        self._pgm_and_args = pgm_and_args
        self._stdin = stdin
        self._transformation = transformation

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._pgm_and_args.tokenization(),
            OptionalAbsStx(self._stdin,
                           self._stdin_tokenizer).tokenization(),
            OptionalAbsStx(self._transformation,
                           self._transformation_tokenizer).tokenization(),
        ])

    @staticmethod
    def _stdin_tokenizer(string_source: TokenSequence) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.new_line(),
            token_sequences.OptionWMandatoryValue.of_option_name(
                syntax_elements.STDIN_OPTION_NAME,
                string_source,
            ),
        ])

    @staticmethod
    def _transformation_tokenizer(transformer: TokenSequence) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.new_line(),
            token_sequences.OptionWMandatoryValue.of_option_name(
                syntax_elements.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                transformer,
            ),
        ])


class ProgramOfExecutableFileCommandLineAbsStx(PgmAndArgsAbsStx):
    def __init__(self,
                 executable_file: PathAbsStx,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.executable_file = executable_file
        self._arguments = ArgumentsAbsStx(arguments)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.executable_file.tokenization(),
            self._arguments.tokenization(),
        ])


class ProgramOfSystemCommandLineAbsStx(PgmAndArgsAbsStx):
    def __init__(self,
                 system_command: NonHereDocStringAbsStx,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.system_command = system_command
        self._arguments = ArgumentsAbsStx(arguments)

    @staticmethod
    def of_str(system_command: str,
               arguments: Sequence[ArgumentAbsStx] = (),
               ) -> PgmAndArgsAbsStx:
        return ProgramOfSystemCommandLineAbsStx(
            str_abs_stx.StringLiteralAbsStx(system_command),
            arguments,
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SYSTEM_PROGRAM_TOKEN),
            self.system_command.tokenization(),
            self._arguments.tokenization(),
        ])


class ProgramOfPythonInterpreterAbsStx(PgmAndArgsAbsStx):
    def __init__(self, arguments: Sequence[ArgumentAbsStx]):
        self._arguments = ArgumentsAbsStx(arguments)

    @staticmethod
    def of_execute_python_src_string(py_src: str) -> PgmAndArgsAbsStx:
        return ProgramOfPythonInterpreterAbsStx([
            ArgumentOfStringAbsStx.of_str(python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE),
            ArgumentOfStringAbsStx.of_str(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
            ArgumentOfStringAbsStx.of_str(py_src),
        ])

    @staticmethod
    def of_execute_python_src_file(py_file: PathAbsStx,
                                   arguments: Sequence[ArgumentAbsStx] = (),
                                   ) -> PgmAndArgsAbsStx:
        return ProgramOfPythonInterpreterAbsStx([ArgumentOfExistingPathAbsStx(py_file)] + list(arguments))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            token_sequences.Option.of_option_name(syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME),
            self._arguments.tokenization(),
        ])


class ProgramOfShellCommandLineAbsStx(PgmAndArgsAbsStx):
    def __init__(self, command_line: NonHereDocStringAbsStx):
        self.command_line = command_line

    @staticmethod
    def of_plain_string(command_line: str) -> 'ProgramOfShellCommandLineAbsStx':
        return ProgramOfShellCommandLineAbsStx(str_abs_stx.StringLiteralAbsStx(command_line))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SHELL_COMMAND_TOKEN),
            self.command_line.tokenization(),
        ])


class TransformableProgramAbsStxBuilder:
    def __init__(self, untransformed: PgmAndArgsAbsStx):
        self._untransformed = untransformed

    def without_transformation(self) -> PgmAndArgsAbsStx:
        return self._untransformed

    def with_transformation(self, transformer: StringTransformerAbsStx) -> ProgramAbsStx:
        return FullProgramAbsStx(self._untransformed, transformation=transformer)

    def with_and_without_transformer_cases(self, transformer: StringTransformerAbsStx,
                                           ) -> Sequence[NameAndValue[ProgramAbsStx]]:
        return [
            NameAndValue('without transformation', self.without_transformation()),
            NameAndValue('with transformation', self.with_transformation(transformer)),
        ]


ARBITRARY_TRANSFORMABLE_PROGRAM = ProgramOfSystemCommandLineAbsStx.of_str('system-program')
