from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx


class NewDirArguments(InstructionArgsAbsStx):
    def __init__(self,
                 path: PathAbsStx,
                 contents: fs_abs_stx.DirContentsAbsStx,
                 ):
        self._path = path
        self._contents = contents

    @staticmethod
    def implicitly_empty(path: PathAbsStx) -> 'NewDirArguments':
        return NewDirArguments(path, fs_abs_stx.DirContentsEmptyAbsStx())

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._path.tokenization(),
            self._contents.tokenization(),
        ])
