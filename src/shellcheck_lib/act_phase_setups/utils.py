import pathlib
import subprocess

from shellcheck_lib.general import exception

from shellcheck_lib.general.output import StdFiles


def execute_cmd_and_args(cmd_and_args: list,
                         cwd_dir_path: pathlib.Path,
                         std_files: StdFiles) -> int:
    try:
        return subprocess.call(cmd_and_args,
                               cwd=str(cwd_dir_path),
                               stdin=std_files.stdin,
                               stdout=std_files.output.out,
                               stderr=std_files.output.err)
    except ValueError as ex:
        msg = 'Error executing act phase as subprocess: ' + str(ex)
        raise exception.ImplementationError(msg)
    except OSError as ex:
        msg = 'Error executing act phase as subprocess: ' + str(ex)
        raise exception.ImplementationError(msg)
