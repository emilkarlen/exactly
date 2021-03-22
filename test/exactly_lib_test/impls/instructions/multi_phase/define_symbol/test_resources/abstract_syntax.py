from abc import ABC

from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.impls.test_resources import abstract_syntaxes
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class _DefineSymbolBase(InstructionArgsAbsStx, ABC):
    def __init__(self,
                 symbol_name: str,
                 value_type: ValueType,
                 value: AbstractSyntax,
                 ):
        self.symbol_name = symbol_name
        self.value_type = value_type
        self.value = value

    def _type_and_sym_name_tokens(self) -> TokenSequence:
        return TokenSequence.sequence([
            ANY_TYPE_INFO_DICT[self.value_type].identifier,
            self.symbol_name,
        ])


class DefineSymbolWMandatoryValue(_DefineSymbolBase):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._type_and_sym_name_tokens(),
            abstract_syntaxes.AssignmentOfMandatoryValue(self.value).tokenization(),
        ])


class DefineSymbolWOptionalValue(_DefineSymbolBase):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._type_and_sym_name_tokens(),
            abstract_syntaxes.AssignmentOfOptionalValue(self.value).tokenization(),
        ])
