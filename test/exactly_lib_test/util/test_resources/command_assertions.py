import sys

import pathlib
from typing import List

from exactly_lib.util.process_execution.command import Command, CommandDriver
from exactly_lib.util.process_execution.commands import CommandDriverForShell, CommandDriverForSystemProgram, \
    CommandDriverForExecutableFile
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equals_executable_file_command_driver(expected: CommandDriverForExecutableFile
                                          ) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with__many(CommandDriverForExecutableFile,
                                       [
                                          asrt.sub_component('executable_file',
                                                             CommandDriverForExecutableFile.executable_file.fget,
                                                             asrt.equals(expected.executable_file)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(False)
                                                             ),
                                      ])


def equals_system_program_command_driver(expected: CommandDriverForSystemProgram
                                         ) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with__many(CommandDriverForSystemProgram,
                                       [
                                          asrt.sub_component('executable_file',
                                                             CommandDriverForSystemProgram.program.fget,
                                                             asrt.equals(expected.program)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(False)
                                                             ),
                                      ])


def equals_shell_command_driver(expected: CommandDriverForShell) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with__many(CommandDriverForShell,
                                       [
                                          asrt.sub_component('shell_command_line',
                                                             CommandDriverForShell.shell_command_line.fget,
                                                             asrt.equals(expected.shell_command_line)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(True)
                                                             ),
                                      ])


def matches_command(driver: ValueAssertion[CommandDriver],
                    arguments: List[str]) -> ValueAssertion[Command]:
    return asrt.is_instance_with__many(
        Command,
        [
            asrt.sub_component('driver',
                               Command.driver.fget,
                               driver
                               ),
            asrt.sub_component('arguments',
                               Command.arguments.fget,
                               asrt.equals(arguments)
                               ),
        ])


def equals_executable_file_command(executable_file: pathlib.Path,
                                   arguments: List[str]) -> ValueAssertion[Command]:
    return matches_command(equals_executable_file_command_driver(CommandDriverForExecutableFile(executable_file)),
                           arguments)


def equals_system_program_command(program: str,
                                  arguments: List[str]) -> ValueAssertion[Command]:
    return matches_command(equals_system_program_command_driver(CommandDriverForSystemProgram(program)),
                           arguments)


def equals_shell_command(command_line: str,
                         arguments: List[str]) -> ValueAssertion[Command]:
    return matches_command(equals_shell_command_driver(CommandDriverForShell(command_line)),
                           arguments)


def equals_execute_py_source_command(source: str) -> ValueAssertion[Command]:
    return equals_executable_file_command(
        pathlib.Path(sys.executable),
        [python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE, source]
    )


def _get_is_shell(command_driver: CommandDriver) -> bool:
    return command_driver.is_shell
