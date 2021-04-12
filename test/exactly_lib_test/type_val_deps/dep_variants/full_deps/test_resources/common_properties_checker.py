import unittest
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
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
              actual: FullDepsSdv[PRIMITIVE],
              message_builder: MessageBuilder,
              ):
        raise NotImplementedError('abstract method')


class CommonExecutionPropertiesChecker(Generic[PRIMITIVE, OUTPUT], ABC):
    """
    Checks common properties of DDV and primitive objects.

    An instance checks a single DDV object and the derived primitive object.
    """

    @abstractmethod
    def check_ddv(self,
                  put: unittest.TestCase,
                  actual: FullDepsDdv[PRIMITIVE],
                  message_builder: MessageBuilder,
                  ):
        raise NotImplementedError('abstract method')

    @abstractmethod
    def check_primitive(self,
                        put: unittest.TestCase,
                        actual: PRIMITIVE,
                        message_builder: MessageBuilder,
                        ):
        """Checks the primitive before application."""
        raise NotImplementedError('abstract method')

    @abstractmethod
    def check_application_output(self,
                                 put: unittest.TestCase,
                                 actual: OUTPUT,
                                 message_builder: MessageBuilder,
                                 ):
        """Checks the output from application."""
        raise NotImplementedError('abstract method')


class Applier(Generic[PRIMITIVE, INPUT, OUTPUT], ABC):
    @abstractmethod
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: PRIMITIVE,
              resolving_environment: FullResolvingEnvironment,
              input_: INPUT) -> OUTPUT:
        raise NotImplementedError('abstract method')


class ApplierThatDoesNothing(Generic[PRIMITIVE], Applier[PRIMITIVE, None, None]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: PRIMITIVE,
              resolving_environment: FullResolvingEnvironment,
              input_: None) -> None:
        return None


class CommonPropertiesConfiguration(Generic[PRIMITIVE, INPUT, OUTPUT], ABC):
    """
    Defines properties of a single primitive type.

    Defines how primitive objects (of the type) are applied.
    Defines common properties of objects in the XDV hierarchy (for the type).
    """

    @abstractmethod
    def applier(self) -> Applier[PRIMITIVE, INPUT, OUTPUT]:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def new_sdv_checker(self) -> CommonSdvPropertiesChecker[PRIMITIVE]:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def new_execution_checker(self) -> CommonExecutionPropertiesChecker[PRIMITIVE, OUTPUT]:
        raise NotImplementedError('abstract method')
