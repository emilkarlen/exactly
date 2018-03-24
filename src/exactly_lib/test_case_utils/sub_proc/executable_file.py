import pathlib
import stat
from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.object_with_symbol_references import ObjectWithSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_ref_validator import FileRefValidatorBase
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.process_execution.os_process_execution import Command, executable_program_command


class ExecutableFileWithArgs(ObjectWithSymbolReferences):
    def __init__(self,
                 file_reference_resolver: FileRefResolver,
                 arguments: ListResolver):
        self._file_reference_resolver = file_reference_resolver
        self._arguments = arguments
        self._validator = ExistingExecutableFileValidator(file_reference_resolver)

    @property
    def file_resolver(self) -> FileRefResolver:
        return self._file_reference_resolver

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.symbol_usages

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return tuple(self._file_reference_resolver.references) + tuple(self._arguments.references)

    def path(self, environment: PathResolvingEnvironmentPreOrPostSds) -> pathlib.Path:
        return self._file_reference_resolver.resolve_value_of_any_dependency(environment)

    def path_string(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return str(self.path(environment))

    def non_shell_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        cmd_path = self.file_resolver.resolve_value_of_any_dependency(environment)
        cmd_and_args = [str(cmd_path)]
        cmd_and_args.extend(self.arguments.resolve_value_of_any_dependency(environment))

        return executable_program_command(cmd_and_args)


class ExistingExecutableFileValidator(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None
