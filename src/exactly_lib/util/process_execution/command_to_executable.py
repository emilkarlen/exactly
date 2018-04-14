"""
Translation of a :class:`Command` to a class:`Executable`.

The translation depends on the platform.
"""
import platform

from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.process_execution.execution_elements import Executable


def translate(command: Command) -> Executable:
    return _FACTORY_FOR_PLATFORM_SYSTEM_NAME[platform.system()].make(command)


class ExecutableFactory:
    def make(self, command: Command) -> Executable:
        raise NotImplementedError('abstract method')


def get_factory_for_platform_system(platform_system_name: str) -> ExecutableFactory:
    return _FACTORY_FOR_PLATFORM_SYSTEM_NAME[platform_system_name]


class ExecutableFactoryForLinux(ExecutableFactory):
    def make(self, command: Command) -> Executable:
        raise NotImplementedError('abstract method')


class ExecutableFactoryForWindows(ExecutableFactory):
    """
    Factory for Windows.

    Not implemented yet, but included to make clarify design.
    """

    def make(self, command: Command) -> Executable:
        raise NotImplementedError('Windows not supported')


_FACTORY_FOR_PLATFORM_SYSTEM_NAME = {
    'Linux': ExecutableFactoryForLinux(),
    'Windows': ExecutableFactoryForWindows(),
}
