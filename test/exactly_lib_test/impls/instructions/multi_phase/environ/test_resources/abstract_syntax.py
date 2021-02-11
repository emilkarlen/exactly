from abc import ABC
from typing import Optional

from exactly_lib.impls.instructions.multi_phase import env as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.util.test_resources.quoting import Surrounded


class InstructionArgumentsAbsStx(AbstractSyntax, ABC):
    pass


class SetVariableArgumentsAbsStx(InstructionArgumentsAbsStx):
    def __init__(self,
                 var_name: str,
                 value: NonHereDocStringAbsStx,
                 ):
        self.var_name = var_name
        self.value = value

    @staticmethod
    def of_str(var_name: str,
               value: str,
               quoting: Optional[QuoteType] = None,
               ) -> 'SetVariableArgumentsAbsStx':
        return SetVariableArgumentsAbsStx(var_name,
                                          StringLiteralAbsStx(value, quoting))

    @staticmethod
    def of_nav(var_and_val: NameAndValue[str]) -> 'SetVariableArgumentsAbsStx':
        return SetVariableArgumentsAbsStx.of_str(var_and_val.name, var_and_val.value)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(self.var_name),
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(sut.ASSIGNMENT_IDENTIFIER),
            TokenSequence.optional_new_line(),
            self.value.tokenization(),
        ])


class UnsetVariableArgumentsAbsStx(InstructionArgumentsAbsStx):
    def __init__(self, var_name: str):
        self.var_name = var_name

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(sut.UNSET_IDENTIFIER),
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(self.var_name),
        ])


def env_var_ref_syntax(var_name: str) -> str:
    return str(Surrounded('${', '}', var_name))
