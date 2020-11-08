import subprocess
from contextlib import contextmanager
from typing import Optional, Sequence, ContextManager

from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util import functional
from exactly_lib.util.file_utils.std import ProcessExecutionFile


def of_optional(stdin: Optional[StringModel]) -> ContextManager[ProcessExecutionFile]:
    return of_sequence(functional.optional_as_list(stdin))


@contextmanager
def of_sequence(stdin_sequence: Sequence[StringModel]) -> ContextManager[ProcessExecutionFile]:
    if not stdin_sequence:
        yield subprocess.DEVNULL
    elif len(stdin_sequence) == 1:
        model = stdin_sequence[0]
        as_file = model.as_file
        with as_file.open() as f:
            yield f
    else:
        raise NotImplementedError('todo')
