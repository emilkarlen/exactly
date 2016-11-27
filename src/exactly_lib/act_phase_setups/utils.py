import subprocess

from exactly_lib.test_case.act_phase_handling import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.util.failure_details import new_failure_details_from_exception
from exactly_lib.util.process_execution.process_execution_settings import ProcessExecutionSettings, Command
from exactly_lib.util.std import StdFiles


def execute_cmd_and_args(cmd_and_args: list,
                         std_files: StdFiles,
                         process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
    return _execute_sub_process(Command(cmd_and_args, shell=False),
                                std_files,
                                process_execution_settings)


def execute_shell_command(command_line: str,
                          std_files: StdFiles,
                          process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
    return _execute_sub_process(Command(command_line, shell=True),
                                std_files,
                                process_execution_settings)


def _execute_sub_process(command: Command,
                         std_files: StdFiles,
                         process_execution_settings: ProcessExecutionSettings) -> ExitCodeOrHardError:
    try:
        exit_code = subprocess.call(command.args,
                                    timeout=process_execution_settings.timeout_in_seconds,
                                    env=process_execution_settings.environ,
                                    shell=command.shell,
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
    return new_eh_hard_error(new_failure_details_from_exception(ex, message=msg))
