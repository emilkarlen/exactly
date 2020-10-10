import itertools
import pathlib
import unittest
from typing import Optional

from exactly_lib.util.file_utils import dir_file_spaces
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.str_ import sequences


def tmp_dir_file_space_for_test(dir_path: pathlib.Path) -> DirFileSpace:
    file_names = dir_file_spaces.FileNamesConfig(
        '--',
        sequences.int_strings(1, 0),
        (
            sequences.int_strings(1, 0)
            for _ in itertools.count(1)
        )
    )
    return dir_file_spaces.DirFileSpaceAsDirCreatedOnDemand(
        dir_path,
        file_names,
    )


class TmpFileSpaceThatAllowsSinglePathGeneration(DirFileSpaceThatMustNoBeUsed):
    def __init__(self,
                 put: unittest.TestCase,
                 storage_dir: pathlib.Path,
                 path_name: str,
                 ):
        self.put = put
        self.storage_dir = storage_dir
        self.path_name = path_name
        self._path_has_been_generated = False

    def new_path(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        if self._path_has_been_generated:
            self.put.fail('The path has already been generated: {} (suffix "{}")'.format(
                self.path_name,
                name_suffix,
            ))

        self._path_has_been_generated = True

        name = self.path_name
        if name_suffix is not None:
            name = name + name_suffix
        return self.storage_dir / name
