import unittest

from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    Applier
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


class NullApplier(Applier[Program, None, None]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: Program,
              resolving_environment: FullResolvingEnvironment,
              input_: None) -> None:
        pass
