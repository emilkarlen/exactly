import pathlib
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.test_case_utils.string_models.factory import StringModelFactory
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand


@contextmanager
def string_model_factory() -> ContextManager[StringModelFactory]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield StringModelFactory(
            TmpDirFileSpaceAsDirCreatedOnDemand(pathlib.Path(tmp_dir))
        )
