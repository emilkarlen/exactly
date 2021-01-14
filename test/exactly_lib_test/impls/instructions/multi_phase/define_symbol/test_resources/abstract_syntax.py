from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class DefineSymbolWMandatoryValue(AbstractSyntax):
    def __init__(self,
                 symbol_name: str,
                 value_type: ValueType,
                 value: AbstractSyntax,
                 ):
        self.symbol_name = symbol_name
        self.value_type = value_type
        self.value = value

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.sequence([
                ANY_TYPE_INFO_DICT[self.value_type].identifier,
                self.symbol_name,
                '=',
                layout.OPTIONAL_NEW_LINE,
            ]),
            self.value.tokenization(),
        ])
