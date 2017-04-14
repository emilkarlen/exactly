import pathlib
import stat

from exactly_lib.instructions.utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure import file_ref
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_values import FileRefResolver


class ExecutableFile:
    def __init__(self,
                 file_reference_resolver: FileRefResolver,
                 arguments: list):
        self._file_reference_resolver = file_reference_resolver
        self._arguments = arguments
        self._validator = ExistingExecutableFileValidator(file_reference_resolver)

    def path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        fr = self._file_reference_resolver.resolve(environment.value_definitions)
        return fr.file_path_pre_or_post_sds(environment)

    def path_string(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return str(self.path(environment))

    def file_reference(self, symbols: SymbolTable) -> file_ref.FileRef:
        return self._file_reference_resolver.resolve(symbols)

    @property
    def arguments(self) -> list:
        return self._arguments

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        fr = self._file_reference_resolver.resolve(value_definitions)
        return fr.exists_pre_sds(value_definitions)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None
