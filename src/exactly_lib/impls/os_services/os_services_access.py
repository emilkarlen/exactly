import os

from exactly_lib.impls.program_execution import executable_factories
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.os_services import OsServices


class OsServicesError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def new_for_current_os() -> OsServices:
    """
    :raises :class:`OsServicesError`: The current operating system is not supported
    """
    return new_for_os(os.name)


def new_for_os(os_name: str) -> OsServices:
    """
    :raises :class:`OsServicesError`: The given operating system is not supported
    """
    try:
        executable_factory = executable_factories.get_factory_for_operating_system(os_name)
    except KeyError:
        raise OsServicesError(
            'Unsupported Operating System: {}'.format(os_name)
        )
    from ..program_execution.impl import cmd_exe_from_proc_exe
    from exactly_lib.util.process_execution.process_executor import ProcessExecutor
    return new_for_cmd_exe(cmd_exe_from_proc_exe.CommandExecutorFromProcessExecutor(
        ProcessExecutor(),
        executable_factory,
    )
    )


def new_for_cmd_exe(command_executor: CommandExecutor) -> OsServices:
    from . import impl
    return impl.OsServicesForAnyOs(command_executor)
