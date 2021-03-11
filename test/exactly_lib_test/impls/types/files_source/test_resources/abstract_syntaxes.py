from abc import ABC
from typing import Sequence

from exactly_lib.impls.types.files_source import syntax
from exactly_lib.impls.types.files_source.defs import ModificationType, FileType
from exactly_lib.impls.types.files_source.syntax import FILE_TYPE_TOKENS
from exactly_lib.test_case import reserved_words
from exactly_lib.util import collection
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.files_source.test_resources.abstract_syntax import FilesSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx

MODIFICATION_TOKENS = {
    ModificationType.CREATE: TokenSequence.singleton(syntax.EXPLICIT_CREATE),
    ModificationType.APPEND: TokenSequence.singleton(syntax.EXPLICIT_APPEND),
}


class ContentsAbsStx(AbstractSyntax, ABC):
    @staticmethod
    def of_modification(modification: ModificationType,
                        contents: AbstractSyntax,
                        ) -> TokenSequence:
        return TokenSequence.concat([
            MODIFICATION_TOKENS[modification],
            TokenSequence.optional_new_line(),
            contents.tokenization()
        ])


class FileContentsAbsStx(ContentsAbsStx, ABC):
    pass


class FileContentsEmptyAbsStx(FileContentsAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class FileContentsExplicitAbsStx(FileContentsAbsStx):
    def __init__(self,
                 modification: ModificationType,
                 contents: StringSourceAbsStx,
                 ):
        self._modification = modification
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return self.of_modification(self._modification, self._contents)


class DirContentsAbsStx(ContentsAbsStx, ABC):
    pass


class DirContentsEmptyAbsStx(DirContentsAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class DirContentsExplicitAbsStx(DirContentsAbsStx):
    def __init__(self,
                 modification: ModificationType,
                 contents: FilesSourceAbsStx,
                 ):
        self._modification = modification
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return self.of_modification(self._modification, self._contents)


class FileSpecAbsStx(AbstractSyntax, ABC):
    def __init__(self,
                 file_type: FileType,
                 file_name: StringAbsStx,
                 contents: ContentsAbsStx,
                 ):
        self._file_type = file_type
        self._file_name = file_name
        self._contents = contents

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(FILE_TYPE_TOKENS[self._file_type]),
            TokenSequence.optional_new_line(),
            self._file_name.tokenization(),
            self._contents.tokenization(),
        ])


def regular_file_spec(file_name: StringAbsStx,
                      contents: FileContentsAbsStx,
                      ) -> FileSpecAbsStx:
    return FileSpecAbsStx(
        FileType.REGULAR,
        file_name,
        contents
    )


def dir_spec(file_name: StringAbsStx,
             contents: DirContentsAbsStx,
             ) -> FileSpecAbsStx:
    return FileSpecAbsStx(
        FileType.DIR,
        file_name,
        contents
    )


class LiteralFilesSourceAbsStx(FilesSourceAbsStx):
    def __init__(self, files: Sequence[FileSpecAbsStx]):
        self._files = files

    def tokenization(self) -> TokenSequence:
        file_specs = collection.intersperse_list(
            TokenSequence.new_line(),
            [
                fs.tokenization()
                for fs in self._files
            ]
        )
        return TokenSequence.concat([
            TokenSequence.singleton(reserved_words.BRACE_BEGIN),
            TokenSequence.preceded_by_optional_new_line_if_non_empty(
                TokenSequence.concat(file_specs),
            ),
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(reserved_words.BRACE_END),
        ])
