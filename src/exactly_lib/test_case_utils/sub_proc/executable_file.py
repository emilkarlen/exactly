import pathlib
import stat
from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences, \
    references_from_objects_with_symbol_references
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator


class ExecutableFileWithArgsResolver(ObjectWithSymbolReferences):
    def __init__(self,
                 executable_file: FileRefResolver,
                 arguments: ListResolver):
        self._executable_file = executable_file
        self._arguments = arguments
        self._validator = ExistingExecutableFileValidator(executable_file)

    @property
    def executable_file(self) -> FileRefResolver:
        return self._executable_file

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._executable_file,
            self._arguments])


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None
