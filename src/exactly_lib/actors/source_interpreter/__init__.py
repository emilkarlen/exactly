from typing import List

from exactly_lib.actors.source_interpreter import executable_file
from exactly_lib.actors.source_interpreter import shell_command as shell_cmd
from exactly_lib.actors.source_interpreter.source_file_management import SourceInterpreterSetup, \
    StandardSourceFileManager
from exactly_lib.test_case.actor import Actor
from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import Command


def actor(command: Command) -> Actor:
    return _CommandTranslator(command.arguments).visit(command.driver)


class _CommandTranslator(commands.CommandDriverVisitor):
    def __init__(self, arguments: List[str]):
        self.arguments = arguments

    def visit_shell(self, driver: commands.CommandDriverForShell) -> Actor:
        return shell_cmd.Parser(driver.shell_command_line_with_args(self.arguments))

    def visit_executable_file(self, driver: commands.CommandDriverForExecutableFile) -> Actor:
        return executable_file.Parser(SourceInterpreterSetup(StandardSourceFileManager(
            'src',
            str(driver.executable_file),
            self.arguments)))

    def visit_system_program(self, driver: commands.CommandDriverForSystemProgram) -> Actor:
        raise ValueError('Unsupported source interpreter: System Program Command')
