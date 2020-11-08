import pathlib
import tempfile
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.impls.types.string_model.factory import RootStringModelFactory
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


@contextmanager
def string_model_factory() -> ContextManager[RootStringModelFactory]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield RootStringModelFactory(
            tmp_file_spaces.tmp_dir_file_space_for_test(pathlib.Path(tmp_dir))
        )
