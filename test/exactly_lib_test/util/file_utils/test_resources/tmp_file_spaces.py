import itertools
import pathlib

from exactly_lib.util.file_utils import tmp_file_spaces
from exactly_lib.util.file_utils.tmp_file_space import TmpDirFileSpace
from exactly_lib.util.str_ import sequences


def tmp_dir_file_space_for_test(dir_path: pathlib.Path) -> TmpDirFileSpace:
    file_names = tmp_file_spaces.FileNamesConfig(
        sequences.int_strings(1, 0),
        (
            sequences.int_strings(1, 0)
            for _ in itertools.count(1)
        )
    )
    return tmp_file_spaces.TmpDirFileSpaceAsDirCreatedOnDemand(
        dir_path,
        file_names,
    )
