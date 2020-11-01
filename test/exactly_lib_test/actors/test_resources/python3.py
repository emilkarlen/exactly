import pathlib
import sys

from exactly_lib.actors.source_interpreter import actor
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv


def new_actor() -> Actor:
    return actor.actor(
        python_command()
    )


def python_command() -> CommandSdv:
    return command_sdvs.for_executable_file(
        path_sdvs.constant(path_ddvs.absolute_path(pathlib.Path(sys.executable)))
    )
