import sys
from pathlib import Path
from typing import Sequence

from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.commands import CommandDriverForExecutableFile
from exactly_lib_test.test_resources.programs.python_program_execution import \
    PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path


def command_that_runs_py_file(py_src_file: Path, arguments_after_py_file: Sequence[str] = ()) -> Command:
    return Command(
        CommandDriverForExecutableFile(described_path.new_primitive(Path(sys.executable))),
        [str(py_src_file)] + list(arguments_after_py_file)
    )


def command_that_runs_py_src_via_cmd_line(py_src: str) -> Command:
    return Command(
        CommandDriverForExecutableFile(described_path.new_primitive(Path(sys.executable))),
        [PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE, str(py_src)]
    )


def command_that_runs_executable_file(exe_file: Path, arguments: Sequence[str] = ()) -> Command:
    return Command(
        CommandDriverForExecutableFile(described_path.new_primitive(exe_file)),
        list(arguments)
    )
