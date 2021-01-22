from contextlib import contextmanager
from typing import ContextManager, Optional

from exactly_lib.impls.types.string_source import as_stdin
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles


@contextmanager
def of_optional_stdin(stdin: Optional[StringSource],
                      output: StdOutputFiles,
                      ) -> ContextManager[StdFiles]:
    with as_stdin.of_optional(stdin) as stdin_f:
        yield StdFiles(stdin_f, output)
