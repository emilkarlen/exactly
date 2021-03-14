from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


class InstructionAbsStx(InstructionArgsAbsStx):
    def __init__(self,
                 destination: PathAbsStx,
                 contents: fs_abs_stx.FileContentsAbsStx,
                 ):
        self._destination = destination
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._destination.tokenization(),
            self._contents.tokenization(),
        ])


def with_explicit_contents_(destination: PathAbsStx,
                            modification: ModificationType,
                            contents: StringSourceAbsStx,
                            ) -> InstructionAbsStx:
    return InstructionAbsStx(destination,
                             fs_abs_stx.FileContentsExplicitAbsStx(
                                 modification,
                                 contents
                             ))


def create_w_explicit_contents(destination: PathAbsStx,
                               contents: StringSourceAbsStx,
                               ) -> InstructionAbsStx:
    return with_explicit_contents_(destination, ModificationType.CREATE, contents)


def without_contents(destination: PathAbsStx) -> InstructionAbsStx:
    return InstructionAbsStx(destination, fs_abs_stx.FileContentsEmptyAbsStx())
