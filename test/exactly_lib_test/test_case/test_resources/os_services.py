from exactly_lib.impls.os_services import os_services_access
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorWInitialAction
from exactly_lib_test.test_resources import recording


def os_services_w_cmd_exe_counting(counter: recording.Counter) -> OsServices:
    os_services__default = os_services_access.new_for_current_os()
    return os_services_w_cmd_exe_counting__w_wrapped(counter, os_services__default.command_executor)


def os_services_w_cmd_exe_counting__w_wrapped(counter: recording.Counter,
                                              wrapped: CommandExecutor) -> OsServices:
    return os_services_access.new_for_cmd_exe(
        CommandExecutorWInitialAction(
            wrapped,
            initial_action=counter.increase,
        )
    )
