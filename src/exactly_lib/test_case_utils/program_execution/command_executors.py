from typing import TypeVar

from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.program_execution.command_executor import CommandExecutor
from exactly_lib.util.process_execution.process_executor import ExecutableExecutor

T = TypeVar('T')


def executor_that_raises_hard_error(
        os_services: OsServices,
        exe_of_executable: ExecutableExecutor[T]
) -> CommandExecutor[T]:
    from .impl import cmd_exe_w_hard_error
    return cmd_exe_w_hard_error.Executor(
        os_services,
        exe_of_executable,
    )
