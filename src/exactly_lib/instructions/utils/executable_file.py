import pathlib
import stat

from exactly_lib.instructions.utils import file_ref
from exactly_lib.instructions.utils.file_ref import FileRefValidatorBase
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case.phases.common import HomeAndSds


class ExecutableFile:
    def __init__(self,
                 file_reference: file_ref.FileRef,
                 arguments: list):
        self._file_reference = file_reference
        self._arguments = arguments
        self._validator = ExistingExecutableFileValidator(file_reference)

    def path(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self._file_reference.file_path_pre_or_post_sds(home_and_sds)

    def path_string(self, home_and_sds: HomeAndSds) -> str:
        return str(self.path(home_and_sds))

    @property
    def file_reference(self) -> file_ref.FileRef:
        return self._file_reference

    @property
    def arguments(self) -> list:
        return self._arguments

    @property
    def exists_pre_eds(self) -> bool:
        return self._file_reference.exists_pre_eds

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
