import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from exactly_lib.util.process_execution.process_executor import ProcessExecutionFile


@contextmanager
def dev_null() -> ContextManager[ProcessExecutionFile]:
    yield subprocess.DEVNULL


@contextmanager
def open_file(path: Path, mode: str) -> ContextManager[ProcessExecutionFile]:
    with path.open(mode) as f:
        yield f
