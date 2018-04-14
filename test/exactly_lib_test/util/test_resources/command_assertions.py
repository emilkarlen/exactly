import pathlib
import sys

from exactly_lib.util.process_execution.execution_elements import Command, ExecutableFileCommand, \
    ExecutableProgramCommand, ShellCommand
from exactly_lib_test.test_resources.programs import python_program_execution
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_executable_file_command(expected: ExecutableFileCommand) -> asrt.ValueAssertion[Command]:
    return asrt.is_instance_with_many(ExecutableFileCommand,
                                      [
                                          asrt.sub_component('executable_file',
                                                             ExecutableFileCommand.executable_file.fget,
                                                             asrt.equals(expected.executable_file)
                                                             ),
                                          asrt.sub_component('arguments',
                                                             ExecutableFileCommand.arguments.fget,
                                                             asrt.equals(expected.arguments)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(False)
                                                             ),
                                      ])


def equals_execute_py_source_command(source: str) -> asrt.ValueAssertion[Command]:
    return equals_executable_file_command(
        ExecutableFileCommand(pathlib.Path(sys.executable),
                              [python_program_execution.PY_ARG_FOR_EXECUTING_SOURCE_ON_COMMAND_LINE,
                               source])
    )


def equals_executable_program_command(expected: ExecutableProgramCommand) -> asrt.ValueAssertion[Command]:
    return asrt.is_instance_with_many(ExecutableProgramCommand,
                                      [
                                          asrt.sub_component('executable_file',
                                                             ExecutableProgramCommand.program.fget,
                                                             asrt.equals(expected.program)
                                                             ),
                                          asrt.sub_component('arguments',
                                                             ExecutableProgramCommand.arguments.fget,
                                                             asrt.equals(expected.arguments)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(False)
                                                             ),
                                      ])


def equals_shell_command(expected: ShellCommand) -> asrt.ValueAssertion[Command]:
    return asrt.is_instance_with_many(ShellCommand,
                                      [
                                          asrt.sub_component('shell_command_line',
                                                             ShellCommand.shell_command_line.fget,
                                                             asrt.equals(expected.shell_command_line)
                                                             ),
                                          asrt.sub_component('shell',
                                                             _get_is_shell,
                                                             asrt.equals(True)
                                                             ),
                                      ])


def _get_is_shell(command: Command) -> bool:
    return command.shell
