from abc import ABC

from exactly_lib.definitions import instruction_arguments
from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


class ContentsVariantAbsStx(AbstractSyntax, ABC):
    pass


class ImplicitlyEmptyContentsVariantAbsStx(ContentsVariantAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class ExplicitContentsVariantAbsStx(ContentsVariantAbsStx):
    def __init__(self, contents: StringSourceAbsStx):
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(instruction_arguments.ASSIGNMENT_OPERATOR),
            TokenSequence.optional_new_line(),
            self._contents.tokenization(),
        ])


class CustomExplicitContentsVariantAbsStx(ContentsVariantAbsStx):
    def __init__(self, contents: TokenSequence):
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(instruction_arguments.ASSIGNMENT_OPERATOR),
            TokenSequence.optional_new_line(),
            self._contents,
        ])


class InstructionAbsStx(InstructionArgsAbsStx):
    def __init__(self,
                 destination: PathAbsStx,
                 contents: ContentsVariantAbsStx,
                 ):
        self._destination = destination
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._destination.tokenization(),
            self._contents.tokenization(),
        ])


def with_explicit_contents(destination: PathAbsStx,
                           contents: StringSourceAbsStx,
                           ) -> InstructionAbsStx:
    return InstructionAbsStx(destination, ExplicitContentsVariantAbsStx(contents))


def without_contents(destination: PathAbsStx) -> InstructionAbsStx:
    return InstructionAbsStx(destination, ImplicitlyEmptyContentsVariantAbsStx())
