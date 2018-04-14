"""
Translation of a :class:`Command` to a class:`Executable`.

The translation depends on the platform.
"""
import os

from exactly_lib.util.process_execution import commands
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.process_execution.executable_factory import ExecutableFactory
from exactly_lib.util.process_execution.execution_elements import Executable


def get_factory_for_operating_system(os_module_name: str) -> ExecutableFactory:
    return _FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME[os_module_name]


def get_factory_for_current_operating_system() -> ExecutableFactory:
    try:
        return _FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME[os.name]
    except KeyError:
        return ExecutableFactoryForUnsupportedSystem()


class ExecutableFactoryBase(ExecutableFactory):
    def __init__(self):
        self._translator = _CommandTranslator()

    def make(self, command: Command) -> Executable:
        return self._translator.visit(command)


class ExecutableFactoryForPosix(ExecutableFactoryBase):
    pass


class ExecutableFactoryForWindows(ExecutableFactoryBase):
    """
    Factory for Windows.

    Not implemented yet, but included to make clarify design.
    """

    def make(self, command: Command) -> Executable:
        pass


class ExecutableFactoryForUnsupportedSystem(ExecutableFactory):
    def make(self, command: Command) -> Executable:
        raise NotImplementedError('Unsupported system: ' + os.name)


class _CommandTranslator(commands.CommandVisitor):
    def visit_shell(self, command: commands.ShellCommand) -> Executable:
        return Executable(is_shell=True,
                          arg_list_or_str=command.args)

    def visit_executable_file(self, command: commands.ExecutableFileCommand) -> Executable:
        return Executable(is_shell=False,
                          arg_list_or_str=[str(command.executable_file)] + command.arguments)

    def visit_system_program(self, command: commands.SystemProgramCommand) -> Executable:
        return Executable(is_shell=False,
                          arg_list_or_str=[command.program] + command.arguments)


_FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME = {
    'posix': ExecutableFactoryForPosix(),
    'nt': ExecutableFactoryForWindows(),
}
