from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.test_resources.abstract_syntax import DataTypeAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx


class IntegerAbsStx(DataTypeAbsStx):
    def __init__(self, string: StringAbsStx):
        self._string = string

    def tokenization(self) -> TokenSequence:
        return self._string.tokenization()
