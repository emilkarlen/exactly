from exactly_lib.definitions import instruction_arguments
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class AssignmentOfMandatoryValue(AbstractSyntax):
    def __init__(self, value: AbstractSyntax):
        self.value = value

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.sequence([
                instruction_arguments.ASSIGNMENT_OPERATOR,
                layout.OPTIONAL_NEW_LINE,
            ]),
            self.value.tokenization(),
        ])


class AssignmentOfOptionalValue(AbstractSyntax):
    def __init__(self, value: AbstractSyntax):
        self.value = value

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(
                instruction_arguments.ASSIGNMENT_OPERATOR,
            ),
            self.value.tokenization(),
        ])
