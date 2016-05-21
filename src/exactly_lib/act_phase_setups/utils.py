import subprocess

from exactly_lib.execution.act_phase import ExitCodeOrHardError, new_eh_exit_code, new_eh_hard_error
from exactly_lib.execution.result import new_failure_details_from_exception
from exactly_lib.util.std import StdFiles


def execute_cmd_and_args(cmd_and_args: list,
                         std_files: StdFiles) -> ExitCodeOrHardError:
    try:
        exit_code = subprocess.call(cmd_and_args,
                                    stdin=std_files.stdin,
                                    stdout=std_files.output.out,
                                    stderr=std_files.output.err)
        return new_eh_exit_code(exit_code)
    except ValueError as ex:
        return _exception(ex)
    except OSError as ex:
        return _exception(ex)


def _exception(ex: Exception) -> ExitCodeOrHardError:
    return new_eh_hard_error(new_failure_details_from_exception(ex))
