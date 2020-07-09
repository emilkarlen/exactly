import os
import subprocess

from exactly_lib.definitions.entity import concepts
from exactly_lib.test_case import executable_factories
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.test_case.result.eh import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.result.failure_details import FailureDetails
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings


class AtcSubProcessExecutor(AtcOsProcessExecutor):
    def __init__(self, executable_factory: ExecutableFactory):
        self._executable_factory = executable_factory

    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        executable = self._executable_factory.make(command)
        try:
            exit_code = subprocess.call(executable.arg_list_or_str,
                                        timeout=process_execution_settings.timeout_in_seconds,
                                        env=process_execution_settings.environ,
                                        shell=executable.is_shell,
                                        stdin=std_files.stdin,
                                        stdout=std_files.output.out,
                                        stderr=std_files.output.err)
            return new_eh_exit_code(exit_code)
        except ValueError as ex:
            return self._exception(ex)
        except OSError as ex:
            return self._exception(ex)
        except subprocess.TimeoutExpired as ex:
            return self._exception(ex)

    @staticmethod
    def _exception(ex: Exception) -> ExitCodeOrHardError:
        msg = 'Error executing {atc} in sub process.'.format(atc=concepts.ACTION_TO_CHECK_CONCEPT_INFO.singular_name)
        return new_eh_hard_error(FailureDetails.new_exception(ex, message=msg))


class _AtcSubProcessExecutorForUnsupportedOperatingSystem(AtcOsProcessExecutor):
    def execute(self,
                command: Command,
                std_files: StdFiles,
                process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
        raise ValueError('System not supported: ' + os.name)


def _atc_os_process_executor_for_current_system() -> AtcOsProcessExecutor:
    try:
        executable_factory = executable_factories.get_factory_for_operating_system(os.name)
        return AtcSubProcessExecutor(executable_factory)
    except KeyError:
        return _AtcSubProcessExecutorForUnsupportedOperatingSystem()


DEFAULT_ATC_OS_PROCESS_EXECUTOR = _atc_os_process_executor_for_current_system()
