from abc import ABC

from exactly_lib.definitions.formatting import SectionName
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class SectionDocElementAbStx(AbstractSyntax, ABC):
    pass


class SectionHeaderAbStx(SectionDocElementAbStx):
    def __init__(self, name: str):
        self._name = name

    def tokenization(self) -> TokenSequence:
        return TokenSequence.singleton(
            SectionName(self._name).syntax
        )


class NamedInstruction(SectionDocElementAbStx):
    def __init__(self,
                 name: str,
                 argument: AbstractSyntax,
                 ):
        self._name = name
        self._argument = argument

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(self._name),
            self._argument.tokenization(),
        ])
