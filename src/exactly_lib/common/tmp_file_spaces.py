import pathlib
from typing import Iterator

from exactly_lib.util.file_utils import tmp_file_spaces
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.str_ import sequences


def std_tmp_dir_file_space(dir_path: pathlib.Path) -> TmpDirFileSpace:
    return tmp_file_spaces.TmpDirFileSpaceAsDirCreatedOnDemand(
        dir_path,
        tmp_file_spaces.FileNamesConfig(
            std_tmp_dir_file_names(),
            _std_tmp_sub_dir_file_names(),
        ),
    )


def std_tmp_dir_file_names() -> Iterator[str]:
    return sequences.int_strings(1, 2)


def _std_tmp_sub_dir_file_names() -> Iterator[Iterator[str]]:
    while True:
        yield std_tmp_dir_file_names()
