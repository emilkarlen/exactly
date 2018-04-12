from exactly_lib.util.process_execution.os_process_execution import Command, ExecutableFileCommand, \
    ExecutableProgramCommand, ShellCommand
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
