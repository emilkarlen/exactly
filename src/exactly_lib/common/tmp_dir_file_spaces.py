import pathlib
from typing import Iterator

from exactly_lib.util.file_utils import dir_file_spaces
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.str_ import sequences


def std_tmp_dir_file_space(dir_path: pathlib.Path) -> DirFileSpace:
    return dir_file_spaces.DirFileSpaceAsDirCreatedOnDemand(
        dir_path,
        dir_file_spaces.FileNamesConfig(
            '-',
            std_tmp_dir_file_names(),
            _std_tmp_sub_dir_file_names(),
        ),
    )


def std_tmp_dir_file_names() -> Iterator[str]:
    return sequences.int_strings(1, 2)


def _std_tmp_sub_dir_file_names() -> Iterator[Iterator[str]]:
    while True:
        yield std_tmp_dir_file_names()


def instruction_dir_name(instruction_number: int) -> str:
    return str(instruction_number).zfill(2)
