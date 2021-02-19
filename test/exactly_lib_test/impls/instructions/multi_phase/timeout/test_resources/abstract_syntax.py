from exactly_lib.impls.instructions.multi_phase.timeout import defs
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx


class InstructionArgumentsAbsStx(AbstractSyntax):
    def __init__(self, value: NonHereDocStringAbsStx):
        self._value = value

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(defs.ASSIGNMENT_IDENTIFIER),
            TokenSequence.optional_new_line(),
            self._value.tokenization(),
        ])


SYNTAX_ERROR_ARGUMENTS = (
    CustomAbsStx.empty(),
    StringLiteralAbsStx('arg1 arg2'),
    InstructionArgumentsAbsStx(StringLiteralAbsStx('arg1 arg2')),
)
INVALID_INT_VALUES = [
    'notAnInteger',
    '-1',
    '1-2',
    '5/2',
    '"hello"',
]
