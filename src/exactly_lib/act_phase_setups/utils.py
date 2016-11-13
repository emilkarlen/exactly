import subprocess

from exactly_lib.instructions.utils.sub_process_execution import ProcessExecutionSettings
from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.util.failure_details import new_failure_details_from_exception
from exactly_lib.util.std import StdFiles


def settings_from_env(environment: InstructionEnvironmentForPreSdsStep) -> ProcessExecutionSettings:
    return ProcessExecutionSettings(timeout_in_seconds=environment.timeout_in_seconds,
                                    environ=environment.environ)


def execute_cmd_and_args(cmd_and_args: list,
                         std_files: StdFiles,
                         process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
    return _execute_sub_process(cmd_and_args, std_files, process_execution_settings)


def execute_shell_command(command_line: str,
                          std_files: StdFiles,
                          process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
    return _execute_sub_process(command_line, std_files, process_execution_settings, shell=True)


def _execute_sub_process(args,
                         std_files: StdFiles,
                         process_execution_settings: ProcessExecutionSettings,
                         shell=False) -> ExitCodeOrHardError:
    try:
        exit_code = subprocess.call(args,
                                    timeout=process_execution_settings.timeout_in_seconds,
                                    env=process_execution_settings.environ,
                                    shell=shell,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)
    except ValueError as ex:
        return _exception(ex)
    except OSError as ex:
        return _exception(ex)
    except subprocess.TimeoutExpired as ex:
        return _exception(ex)


def _exception(ex: Exception) -> ExitCodeOrHardError:
    msg = 'Error executing act program in sub process.'
    return new_eh_hard_error(new_failure_details_from_exception(ex,
                                                                message=msg))
