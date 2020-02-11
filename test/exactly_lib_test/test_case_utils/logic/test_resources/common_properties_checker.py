import unittest
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder

PRIMITIVE = TypeVar('PRIMITIVE')
INPUT = TypeVar('INPUT')
OUTPUT = TypeVar('OUTPUT')


class CommonSdvPropertiesChecker(Generic[PRIMITIVE], ABC):
    """
    Checks common properties of SDV objects.
    """

    @abstractmethod
    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        pass


class CommonExecutionPropertiesChecker(Generic[PRIMITIVE], ABC):
    """
    Checks common properties of DDV and primitive objects.

    An instance checks a single DDV object and the derived primitive object.
    """

    @abstractmethod
    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: LogicDdv[PRIMITIVE],
                  message_builder: MessageBuilder,
                  ):
        pass

    @abstractmethod
    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: PRIMITIVE,
                        message_builder: MessageBuilder):
        """Checks the primitive before application."""
        pass


class CommonPropertiesConfiguration(Generic[PRIMITIVE, INPUT, OUTPUT], ABC):
    """
    Defines properties of a single primitive type.

    Defines how primitive objects (of the type) are applied.
    Defines common properties of objects in the XDV hierarchy (for the type).
    """

    @abstractmethod
    def apply(self,
              primitive: PRIMITIVE,
              resolving_environment: FullResolvingEnvironment,
              input_: INPUT) -> OUTPUT:
        pass

    @abstractmethod
    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[PRIMITIVE]:
        pass

    @abstractmethod
    def new_execution_checker(self) -> CommonExecutionPropertiesChecker[PRIMITIVE]:
        pass
