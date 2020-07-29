from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


def application_environment_for_test(
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        os_services_: OsServices = os_services_access.new_for_current_os(),
        process_execution_settings: ProcessExecutionSettings = execution_elements.with_no_timeout(),
) -> ApplicationEnvironment:
    return ApplicationEnvironment(os_services_, process_execution_settings, tmp_file_space)
