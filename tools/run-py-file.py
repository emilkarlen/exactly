import path_and_cwd_setup

path_and_cwd_setup.initialize()

import sys
import pathlib

def exit_err(msg: str):
    print(msg,file=sys.stderr)
    exit(1)

if len(sys.argv) != 2:
    exit_err('Usage FILE')

file_to_run = pathlib.Path(sys.argv[1])

if not file_to_run.is_file():
    exit_err('Not a file: ' + str(file_to_run))

exec(file_to_run.open().read())
