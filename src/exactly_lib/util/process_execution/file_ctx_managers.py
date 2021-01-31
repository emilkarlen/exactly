import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, TextIO

from exactly_lib.util.file_utils.std import ProcessExecutionFile


@contextmanager
def dev_null() -> ContextManager[ProcessExecutionFile]:
    yield subprocess.DEVNULL


@contextmanager
def open_file(path: Path, mode: str) -> ContextManager[ProcessExecutionFile]:
    with path.open(mode) as f:
        yield f


@contextmanager
def opened_file(f: TextIO) -> ContextManager[ProcessExecutionFile]:
    yield f
