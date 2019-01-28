import pathlib

from exactly_lib.util.file_utils import TmpDirFileSpace


class TmpDirFileSpaceThatMustNoBeUsed(TmpDirFileSpace):
    def new_path(self) -> pathlib.Path:
        raise NotImplementedError('must not be used')

    def new_path_as_existing_dir(self) -> pathlib.Path:
        raise NotImplementedError('must not be used')
