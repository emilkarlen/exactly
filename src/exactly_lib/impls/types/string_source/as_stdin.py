import subprocess
from contextlib import contextmanager
from typing import Optional, Sequence, ContextManager

from exactly_lib.type_val_prims.string_source.impls import concat
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import ProcessExecutionFile


def of_optional(stdin: Optional[StringSource]) -> ContextManager[ProcessExecutionFile]:
    return _context_manager(stdin)


def of_sequence(stdin_parts: Sequence[StringSource],
                mem_buff_size: int) -> ContextManager[ProcessExecutionFile]:
    return _context_manager(concat.string_source_of_mb_empty_sequence(stdin_parts, mem_buff_size, 'stdin'))


@contextmanager
def _context_manager(contents: Optional[StringSource]) -> ContextManager[ProcessExecutionFile]:
    if contents is None:
        yield subprocess.DEVNULL
    else:
        as_file = contents.contents().as_file
        with as_file.open() as f:
            yield f
