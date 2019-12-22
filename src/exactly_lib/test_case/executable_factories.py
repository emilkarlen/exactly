"""
Translation of a :class:`Command` to a class:`Executable`.

The translation depends on the platform.
"""
import os
from typing import List

from exactly_lib.test_case.executable_factory import ExecutableFactory
from exactly_lib.type_system.logic.program.process_execution import commands
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import Executable


def get_factory_for_operating_system(os_module_name: str) -> ExecutableFactory:
    return _FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME[os_module_name]


def get_factory_for_current_operating_system() -> ExecutableFactory:
    try:
        return _FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME[os.name]
    except KeyError:
        return ExecutableFactoryForUnsupportedSystem()


class ExecutableFactoryBase(ExecutableFactory):
    def make(self, command: Command) -> Executable:
        return _CommandTranslator(command.arguments).visit(command.driver)


class ExecutableFactoryForPosix(ExecutableFactoryBase):
    pass


class ExecutableFactoryForWindows(ExecutableFactoryBase):
    pass


class ExecutableFactoryForUnsupportedSystem(ExecutableFactory):
    def make(self, command: Command) -> Executable:
        raise NotImplementedError('Unsupported system: ' + os.name)


class _CommandTranslator(commands.CommandDriverVisitor):
    def __init__(self, arguments: List[str]):
        self.arguments = arguments

    def visit_shell(self, driver: commands.CommandDriverForShell) -> Executable:
        return Executable(is_shell=True,
                          arg_list_or_str=driver.shell_command_line_with_args(self.arguments))

    def visit_executable_file(self, driver: commands.CommandDriverForExecutableFile) -> Executable:
        return Executable(is_shell=False,
                          arg_list_or_str=[str(driver.executable_file)] + self.arguments)

    def visit_system_program(self, driver: commands.CommandDriverForSystemProgram) -> Executable:
        return Executable(is_shell=False,
                          arg_list_or_str=[driver.program] + self.arguments)


_FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME = {
    'posix': ExecutableFactoryForPosix(),
    'nt': ExecutableFactoryForWindows(),
}
