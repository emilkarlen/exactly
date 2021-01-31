import pathlib
import sys
from typing import List, Sequence

from exactly_lib.type_val_deps.types.path.path_ddv import DescribedPath
from exactly_lib.type_val_prims.program.command import Command, CommandDriver
from exactly_lib.type_val_prims.program.commands import CommandDriverForShell, \
    CommandDriverForSystemProgram, \
    CommandDriverForExecutableFile
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.path.test_resources.described_path import new_primitive


def equals_executable_file_command_driver(expected: CommandDriverForExecutableFile
                                          ) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForExecutableFile,
        asrt.sub_component('executable_file',
                           CommandDriverForExecutableFile.executable_file.fget,
                           asrt.equals(expected.executable_file)
                           )
    )


def matches_executable_file_command_driver(executable: Assertion[pathlib.Path],
                                           ) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForExecutableFile,
        asrt.sub_component('executable_file',
                           CommandDriverForExecutableFile.executable_file.fget,
                           asrt.is_instance_with(pathlib.Path, executable)
                           ),
    )


def equals_system_program_command_driver(expected: CommandDriverForSystemProgram
                                         ) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForSystemProgram,
        asrt.sub_component('executable_file',
                           CommandDriverForSystemProgram.program.fget,
                           asrt.equals(expected.program)
                           )
    )


def matches_system_program_command_driver(program: Assertion[str],
                                          ) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForSystemProgram,
        asrt.sub_component('program',
                           CommandDriverForSystemProgram.program.fget,
                           program
                           ),
    )


def equals_shell_command_driver(expected: CommandDriverForShell) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForShell,
        asrt.sub_component('shell_command_line',
                           CommandDriverForShell.shell_command_line.fget,
                           asrt.equals(expected.shell_command_line)
                           )
    )


def matches_shell_command_driver(shell_command_line: Assertion[str]) -> Assertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForShell,
        asrt.sub_component(
            'shell_command_line',
            CommandDriverForShell.shell_command_line.fget,
            shell_command_line
        ))


def matches_command(driver: Assertion[CommandDriver],
                    arguments: Assertion[Sequence[str]]) -> Assertion[Command]:
    return asrt.is_instance_with__many(
        Command,
        [
            asrt.sub_component('driver',
                               Command.driver.fget,
                               driver
                               ),
            asrt.sub_component('arguments',
                               Command.arguments.fget,
                               arguments
                               ),
        ])


def equals_executable_file_command(executable_file: DescribedPath,
                                   arguments: List[str]) -> Assertion[Command]:
    return matches_command(
        equals_executable_file_command_driver(CommandDriverForExecutableFile(executable_file)),
        asrt.equals(arguments),
    )


def equals_system_program_command(program: str,
                                  arguments: List[str]) -> Assertion[Command]:
    return matches_command(
        equals_system_program_command_driver(CommandDriverForSystemProgram(program)),
        asrt.equals(arguments),
    )


def equals_shell_command(command_line: str,
                         arguments: List[str]) -> Assertion[Command]:
    return matches_command(
        equals_shell_command_driver(CommandDriverForShell(command_line)),
        asrt.equals(arguments),
    )


def equals_execute_py_source_command(source: str) -> Assertion[Command]:
    return equals_executable_file_command(
        new_primitive(pathlib.Path(sys.executable)),
        [python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE, source]
    )
