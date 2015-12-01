import pathlib
import stat

from shellcheck_lib.instructions.utils import file_ref
from shellcheck_lib.instructions.utils import parse_file_ref
from shellcheck_lib.instructions.utils.file_ref import FileRefValidatorBase
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from shellcheck_lib.test_case.sections.common import HomeAndEds


class ExecutableFile:
    def __init__(self,
                 file_reference: file_ref.FileRef,
                 arguments: list):
        self._file_reference = file_reference
        self._arguments = arguments
        self._validator = ExistingExecutableFile(file_reference)

    def path(self, home_and_eds: HomeAndEds) -> pathlib.Path:
        return self._file_reference.file_path_pre_or_post_eds(home_and_eds)

    def path_string(self, home_and_eds: HomeAndEds) -> str:
        return str(self.path(home_and_eds))

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
    def validator(self) -> PreOrPostEdsValidator:
        return self._validator


def parse(tokens0: TokenStream) -> (ExecutableFile, TokenStream):
    """
    :param tokens0: instruction argument
    :raise SingleInstructionInvalidArgumentException: Invalid file syntax
    """
    (the_file_ref, remaining_tokens) = parse_file_ref.parse_file_ref(tokens0)
    return ExecutableFile(the_file_ref, []), remaining_tokens


class ExistingExecutableFile(FileRefValidatorBase):
    def _validate_path(self, file_path: pathlib.Path) -> str:
        if not file_path.is_file():
            return 'File does not exist: {}'.format(file_path)
        stat_value = file_path.stat()
        mode = stat_value.st_mode
        if not mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return 'File is not executable. Mode is {}: {}'.format(stat.filemode(mode), file_path)
        return None
