"""
Translation of a :class:`Command` to a class:`Executable`.

The translation depends on the platform.
"""
import os

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
    def make(self, command: Command) -> Executable:
        return Executable(command.shell,
                          command.args)


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


_FACTORY_FOR_OPERATING_SYSTEM_MODULE_NAME = {
    'posix': ExecutableFactoryForPosix(),
    'nt': ExecutableFactoryForWindows(),
}
