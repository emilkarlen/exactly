import pathlib
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.test_case_utils.string_models.factory import StringModelFactory
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


@contextmanager
def string_model_factory() -> ContextManager[StringModelFactory]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield StringModelFactory(
            tmp_file_spaces.tmp_dir_file_space_for_test(pathlib.Path(tmp_dir))
        )
