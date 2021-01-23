from abc import ABC
from typing import Sequence

from exactly_lib.impls.types.program import syntax_elements
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentsAbsStx


class ProgramAbsStx(AbstractSyntax, ABC):
    pass


class PgmAndArgsAbsStx(ProgramAbsStx, ABC):
    """"A program with just a command and arguments."""
    pass


class ProgramOfSymbolReferenceAbsStx(PgmAndArgsAbsStx):
    def __init__(self,
                 symbol_name: str,
                 arguments: Sequence[ArgumentAbsStx] = (),
                 ):
        self.symbol_name = symbol_name
        self._arguments = ArgumentsAbsStx(arguments)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.SYMBOL_REF_PROGRAM_TOKEN),
            TokenSequence.singleton(self.symbol_name),
            self._arguments.tokenization(),
        ])
