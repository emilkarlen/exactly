import pathlib
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.test_case_utils.string_matcher.file_model import DestinationFilePathGetter
from exactly_lib.test_case_utils.string_models.factory import StringModelFactory
from exactly_lib.util.file_utils import TmpFileSpace, TmpDirFileSpaceAsDirCreatedOnDemand


@contextmanager
def destination_file_path_getter_that_gives_seq_of_unique_paths() -> ContextManager[DestinationFilePathGetter]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield _DestinationFilePathGetter(pathlib.Path(tmp_dir))


@contextmanager
def string_model_factory() -> ContextManager[StringModelFactory]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield StringModelFactory(
            TmpDirFileSpaceAsDirCreatedOnDemand(pathlib.Path(tmp_dir))
        )


class _DestinationFilePathGetter(DestinationFilePathGetter):
    def __init__(self, tmp_dir: pathlib.Path):
        super().__init__()
        self.tmp_dir = tmp_dir
        self._file_num = 0

    def get(self,
            tmp_file_space: TmpFileSpace,
            src_file_path: pathlib.Path) -> pathlib.Path:
        self._file_num += 1
        return self.tmp_dir / (str(self._file_num) + '.txt')
