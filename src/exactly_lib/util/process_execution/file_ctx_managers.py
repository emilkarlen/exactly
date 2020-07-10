import subprocess
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.util.process_execution.process_executor import ProcessExecutionFile


@contextmanager
def dev_null() -> ContextManager[ProcessExecutionFile]:
    yield subprocess.DEVNULL
