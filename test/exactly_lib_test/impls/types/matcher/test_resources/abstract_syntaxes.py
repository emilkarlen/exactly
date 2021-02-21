from exactly_lib.definitions import logic
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class NegationMatcherAbsStx(AbstractSyntax):
    def __init__(self, operand: AbstractSyntax):
        self.operand = operand

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(logic.NOT_OPERATOR_NAME),
            self.operand.tokenization(),
        ])


class ConstantMatcherAbsStx(AbstractSyntax):
    def __init__(self, constant: bool):
        self.constant = constant

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([
            logic.CONSTANT_MATCHER,
            logic.BOOLEANS[self.constant],
        ])
