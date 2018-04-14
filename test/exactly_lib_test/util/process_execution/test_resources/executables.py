from typing import Sequence

from exactly_lib.util.process_execution.execution_elements import Executable


def for_executable_file(file_path_or_name,
                        arguments: Sequence[str] = ()) -> Executable:
    return Executable(False,
                      [str(file_path_or_name)] + list(arguments))
