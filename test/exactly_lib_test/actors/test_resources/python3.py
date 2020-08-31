import pathlib
import sys

from exactly_lib.actors.source_interpreter import actor
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_system.data import paths


def new_actor() -> Actor:
    return actor.actor(
        python_command()
    )


def python_command() -> CommandSdv:
    return command_sdvs.for_executable_file(
        path_sdvs.constant(paths.absolute_path(pathlib.Path(sys.executable)))
    )
