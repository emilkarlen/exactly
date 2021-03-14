from abc import ABC
from typing import Sequence

from exactly_lib.impls.types.files_source import syntax
from exactly_lib.impls.types.files_source.defs import ModificationType, FileType
from exactly_lib.impls.types.files_source.syntax import FILE_TYPE_TOKENS
from exactly_lib.util import collection
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.files_source.test_resources.abstract_syntax import FilesSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx

MODIFICATION_TOKENS = {
    ModificationType.CREATE: TokenSequence.singleton(syntax.EXPLICIT_CREATE),
    ModificationType.APPEND: TokenSequence.singleton(syntax.EXPLICIT_APPEND),
}


class ContentsAbsStx(AbstractSyntax, ABC):
    @staticmethod
    def of_modification(modification: TokenSequence,
                        contents: AbstractSyntax,
                        ) -> TokenSequence:
        return TokenSequence.concat([
            modification,
            TokenSequence.optional_new_line(),
            contents.tokenization()
        ])

    @staticmethod
    def of_modification_type(modification: ModificationType,
                             contents: AbstractSyntax,
                             ) -> TokenSequence:
        return ContentsAbsStx.of_modification(
            MODIFICATION_TOKENS[modification],
            contents,
        )


class CustomContentsAbsStx(ContentsAbsStx, ABC):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    def tokenization(self) -> TokenSequence:
        return self._tokens


class FileContentsAbsStx(ContentsAbsStx, ABC):
    pass


class FileCustomContentsAbsStx(FileContentsAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    def tokenization(self) -> TokenSequence:
        return self._tokens


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
        return self.of_modification_type(self._modification, self._contents)


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
        return self.of_modification_type(self._modification, self._contents)


class FileSpecAbsStx(AbstractSyntax, ABC):
    def __init__(self,
                 file_type: str,
                 file_name: StringAbsStx,
                 contents: ContentsAbsStx,
                 ):
        self._file_type = file_type
        self._file_name = file_name
        self._contents = contents

    @staticmethod
    def of_file_type(
            file_type: FileType,
            file_name: StringAbsStx,
            contents: ContentsAbsStx,

    ) -> 'FileSpecAbsStx':
        return FileSpecAbsStx(
            FILE_TYPE_TOKENS[file_type],
            file_name,
            contents,
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(self._file_type),
            TokenSequence.optional_new_line(),
            self._file_name.tokenization(),
            self._contents.tokenization(),
        ])


def regular_file_spec(file_name: StringAbsStx,
                      contents: FileContentsAbsStx,
                      ) -> FileSpecAbsStx:
    return FileSpecAbsStx.of_file_type(
        FileType.REGULAR,
        file_name,
        contents
    )


def regular_file_spec__str_name(file_name: str,
                                contents: FileContentsAbsStx,
                                ) -> FileSpecAbsStx:
    return regular_file_spec(
        StringLiteralAbsStx(file_name),
        contents
    )


def dir_spec(file_name: StringAbsStx,
             contents: DirContentsAbsStx,
             ) -> FileSpecAbsStx:
    return FileSpecAbsStx.of_file_type(
        FileType.DIR,
        file_name,
        contents
    )


def dir_spec__str_name(file_name: str,
                       contents: DirContentsAbsStx,
                       ) -> FileSpecAbsStx:
    return dir_spec(
        StringLiteralAbsStx(file_name),
        contents
    )


class LiteralFilesSourceAbsStx(FilesSourceAbsStx):
    def __init__(self,
                 files: Sequence[FileSpecAbsStx],
                 delimiter__begin: str = syntax.LITERAL_BEGIN,
                 delimiter__end: str = syntax.LITERAL_END,
                 ):
        self._files = files
        self.delimiter__begin = delimiter__begin
        self.delimiter__end = delimiter__end

    def tokenization(self) -> TokenSequence:
        file_specs = collection.intersperse_list(
            TokenSequence.new_line(),
            [
                fs.tokenization()
                for fs in self._files
            ]
        )
        return TokenSequence.concat([
            TokenSequence.singleton(self.delimiter__begin),
            TokenSequence.preceded_by_optional_new_line_if_non_empty(
                TokenSequence.concat(file_specs),
            ),
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(self.delimiter__end),
        ])
