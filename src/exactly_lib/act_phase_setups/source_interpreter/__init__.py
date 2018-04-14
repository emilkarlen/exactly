from typing import List

from exactly_lib.act_phase_setups.source_interpreter import executable_file
from exactly_lib.act_phase_setups.source_interpreter import shell_command as shell_cmd
from exactly_lib.act_phase_setups.source_interpreter.source_file_management import SourceInterpreterSetup, \
    StandardSourceFileManager
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActSourceAndExecutorConstructor
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import Command


def act_phase_handling(command: Command) -> ActPhaseHandling:
    return ActPhaseHandling(act_source_and_executor_constructor(command))


def act_phase_setup(command: Command) -> ActPhaseSetup:
    return ActPhaseSetup(act_source_and_executor_constructor(command))


def act_source_and_executor_constructor(command: Command) -> ActSourceAndExecutorConstructor:
    return _CommandTranslator(command.arguments).visit(command.driver)


class _CommandTranslator(commands.CommandDriverVisitor):
    def __init__(self, arguments: List[str]):
        self.arguments = arguments

    def visit_shell(self, driver: commands.CommandDriverForShell) -> ActSourceAndExecutorConstructor:
        return shell_cmd.Constructor(driver.shell_command_line_with_args(self.arguments))

    def visit_executable_file(self, driver: commands.CommandDriverForExecutableFile) -> ActSourceAndExecutorConstructor:
        return executable_file.Constructor(SourceInterpreterSetup(StandardSourceFileManager(
            'src',
            str(driver.executable_file),
            self.arguments)))

    def visit_system_program(self, driver: commands.CommandDriverForSystemProgram) -> ActSourceAndExecutorConstructor:
        raise ValueError('Unsupported source interpreter: System Program Command')
