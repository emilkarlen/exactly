from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.os_services import OsServices


def command_executor(os_services: OsServices) -> CommandExecutor:
    from .impl import cmd_exe_from_proc_exe
    return cmd_exe_from_proc_exe.CommandExecutorFromProcessExecutor(
        os_services.process_executor(),
        os_services.executable_factory(),
    )
