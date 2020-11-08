from contextlib import contextmanager
from typing import ContextManager, Optional, Sequence

from exactly_lib.impls.types.string_model import as_stdin
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.std import StdFiles, StdOutputFiles


@contextmanager
def of_optional_stdin(stdin: Optional[StringModel],
                      output: StdOutputFiles,
                      ) -> ContextManager[StdFiles]:
    with as_stdin.of_optional(stdin) as stdin_f:
        yield StdFiles(stdin_f, output)


@contextmanager
def of_sequence_of_stdin(stdin: Sequence[StringModel],
                         output: StdOutputFiles,
                         ) -> ContextManager[StdFiles]:
    with as_stdin.of_sequence(stdin) as stdin_f:
        yield StdFiles(stdin_f, output)
