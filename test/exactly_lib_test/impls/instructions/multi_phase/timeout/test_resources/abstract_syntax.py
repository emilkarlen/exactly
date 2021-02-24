from exactly_lib.impls.instructions.multi_phase.timeout import defs
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx, \
    MISSING_END_QUOTE__SOFT


class InstructionArgumentsAbsStx(AbstractSyntax):
    def __init__(self, value: NonHereDocStringAbsStx):
        self._value = value

    @staticmethod
    def of_int(value: NonHereDocStringAbsStx) -> 'InstructionArgumentsAbsStx':
        return InstructionArgumentsAbsStx(value)

    @staticmethod
    def of_none() -> 'InstructionArgumentsAbsStx':
        return InstructionArgumentsAbsStx(StringLiteralAbsStx(defs.NONE_TOKEN))

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(defs.ASSIGNMENT_IDENTIFIER),
            TokenSequence.optional_new_line(),
            self._value.tokenization(),
        ])


SYNTAX_ERROR_ARGUMENTS = (
    CustomAbsStx.empty(),
    StringLiteralAbsStx('1'),
    StringLiteralAbsStx('1 2'),
    InstructionArgumentsAbsStx.of_int(MISSING_END_QUOTE__SOFT),
    SequenceAbsStx.followed_by_superfluous(
        InstructionArgumentsAbsStx.of_int(StringLiteralAbsStx('1'))
    ),
    SequenceAbsStx.followed_by_superfluous(
        InstructionArgumentsAbsStx.of_none()
    ),
)

INVALID_INT_VALUES = [
    'notAnInteger',
    '-1',
    '1-2',
    '5/2',
    '"hello"',
]
