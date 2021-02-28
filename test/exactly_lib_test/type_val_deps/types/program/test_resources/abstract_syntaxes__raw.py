from typing import Sequence

from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentsAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx


class RawSystemCommandLineAbsStx(AbstractSyntax):
    """A system command, without the leading sys-cmd-token used by "full" programs."""

    def __init__(self,
                 system_command: StringAbsStx,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.system_command = system_command
        self._arguments_sequence = arguments
        self._arguments = ArgumentsAbsStx(arguments)

    @staticmethod
    def of_str(system_command: str,
               arguments: Sequence[ArgumentAbsStx] = (),
               ) -> 'RawSystemCommandLineAbsStx':
        return RawSystemCommandLineAbsStx(
            str_abs_stx.StringLiteralAbsStx(system_command),
            arguments,
        )

    def new_w_additional_arguments(self, arguments: Sequence[ArgumentAbsStx]) -> 'RawSystemCommandLineAbsStx':
        return RawSystemCommandLineAbsStx(
            self.system_command,
            tuple(self._arguments_sequence) + tuple(arguments),
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.system_command.tokenization(),
            self._arguments.tokenization(),
        ])


class RawProgramOfSymbolReferenceAbsStx(AbstractSyntax):
    """A system command, without the leading symbol-program-token used by "full" programs."""

    def __init__(self,
                 symbol_name: str,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.symbol_name = symbol_name
        self.arguments_sequence = arguments
        self._arguments = ArgumentsAbsStx(arguments)

    def new_w_additional_arguments(self, arguments: Sequence[ArgumentAbsStx]) -> 'RawProgramOfSymbolReferenceAbsStx':
        return RawProgramOfSymbolReferenceAbsStx(
            self.symbol_name,
            tuple(self.arguments_sequence) + tuple(arguments),
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(self.symbol_name),
            self._arguments.tokenization(),
        ])
