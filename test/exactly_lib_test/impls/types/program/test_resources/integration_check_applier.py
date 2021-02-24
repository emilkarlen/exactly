import unittest

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_deps.dep_variants.test_resources.full_deps.common_properties_checker import \
    Applier


class NullApplier(Applier[Program, None, None]):
    def apply(self,
              put: unittest.TestCase,
              message_builder: MessageBuilder,
              primitive: Program,
              resolving_environment: FullResolvingEnvironment,
              input_: None) -> None:
        pass
