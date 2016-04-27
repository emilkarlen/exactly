import subprocess

from exactly_lib.util import exception
from exactly_lib.util.std import StdFiles


def execute_cmd_and_args(cmd_and_args: list,
                         std_files: StdFiles) -> int:
    try:
        return subprocess.call(cmd_and_args,
                               stdin=std_files.stdin,
                               stdout=std_files.output.out,
                               stderr=std_files.output.err)
    except ValueError as ex:
        msg = 'Error executing act phase as subprocess: ' + str(ex)
        raise exception.ImplementationError(msg)
    except OSError as ex:
        msg = 'Error executing act phase as subprocess: ' + str(ex)
        raise exception.ImplementationError(msg)
