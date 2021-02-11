import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.util.file_utils.test_resources.tmp_file_spaces import tmp_dir_file_space_for_test


def application_environment_for_test(
        tmp_file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        os_services_: OsServices = os_services_access.new_for_current_os(),
        process_execution_settings: ProcessExecutionSettings = ProcessExecutionSettings.null(),
        mem_buff_size: int = 2 ** 10,
) -> ApplicationEnvironment:
    return ApplicationEnvironment(os_services_, process_execution_settings, tmp_file_space, mem_buff_size)


@contextmanager
def application_environment_with_existing_dir(
        os_services: OsServices = os_services_access.new_for_current_os(),
        process_execution_settings: ProcessExecutionSettings = ProcessExecutionSettings.null(),
        mem_buff_size: int = 2 ** 10,
) -> ContextManager[ApplicationEnvironment]:
    with tempfile.TemporaryDirectory(prefix='exactly') as tmp_dir_name:
        yield application_environment_for_test(
            tmp_dir_file_space_for_test(Path(tmp_dir_name)),
            os_services,
            process_execution_settings,
            mem_buff_size,
        )
