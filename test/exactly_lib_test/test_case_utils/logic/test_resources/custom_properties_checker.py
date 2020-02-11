import unittest
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_system.logic.logic_base_class import LogicDdv
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder

PRIMITIVE = TypeVar('PRIMITIVE')
APPLICATION_INPUT = TypeVar('APPLICATION_INPUT')
OUTPUT = TypeVar('OUTPUT')


class CustomSdvPropertiesChecker(Generic[PRIMITIVE], ABC):
    @abstractmethod
    def check(self,
              put: unittest.TestCase,
              actual: LogicSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        pass


class CustomExecutionPropertiesChecker(Generic[PRIMITIVE], ABC):
    """Checks a single DDV object and the derived primitive object"""

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


class CustomPropertiesCheckerConfiguration(Generic[PRIMITIVE, APPLICATION_INPUT, OUTPUT], ABC):
    @abstractmethod
    def apply(self,
              primitive: PRIMITIVE,
              resolving_environment: FullResolvingEnvironment,
              input_: APPLICATION_INPUT) -> OUTPUT:
        pass

    @abstractmethod
    def new_sdv_checker(self) -> CustomSdvPropertiesChecker[PRIMITIVE]:
        pass

    @abstractmethod
    def new_execution_checker(self) -> CustomExecutionPropertiesChecker[PRIMITIVE]:
        pass
