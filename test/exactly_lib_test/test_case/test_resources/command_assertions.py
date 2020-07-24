import pathlib
import sys
from typing import List, Sequence

from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.program.process_execution.command import Command, CommandDriver
from exactly_lib.type_system.logic.program.process_execution.commands import CommandDriverForShell, \
    CommandDriverForSystemProgram, \
    CommandDriverForExecutableFile
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources.described_path import new_primitive


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


def matches_executable_file_command_driver(executable: ValueAssertion[pathlib.Path],
                                           ) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForExecutableFile,
        asrt.sub_component('executable_file',
                           CommandDriverForExecutableFile.executable_file.fget,
                           asrt.is_instance_with(pathlib.Path, executable)
                           ),
    )


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


def matches_system_program_command_driver(program: ValueAssertion[str],
                                          ) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForSystemProgram,
        asrt.sub_component('program',
                           CommandDriverForSystemProgram.program.fget,
                           program
                           ),
    )


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


def matches_shell_command_driver(shell_command_line: ValueAssertion[str]) -> ValueAssertion[CommandDriver]:
    return asrt.is_instance_with(
        CommandDriverForShell,
        asrt.sub_component(
            'shell_command_line',
            CommandDriverForShell.shell_command_line.fget,
            shell_command_line
        ))


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


def matches_command2(driver: ValueAssertion[CommandDriver],
                     arguments: ValueAssertion[Sequence[str]]) -> ValueAssertion[Command]:
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
        new_primitive(pathlib.Path(sys.executable)),
        [python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE, source]
    )


def _get_is_shell(command_driver: CommandDriver) -> bool:
    return command_driver.is_shell
